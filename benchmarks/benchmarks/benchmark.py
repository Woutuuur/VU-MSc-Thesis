from calendar import c
import json
import subprocess
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from typing_extensions import override
from util.color import ANSIColorCode as C
from benchmarks.compiler import Compiler
from config.options import ConfigOptions
from benchmarks.optimization_level import CustomOptimizationLevel, OptimizationLevel
import shutil


class BenchmarkUnit(Enum):
    EXECUTION_TIME = "ms"
    THROUGHPUT = "ops/sec"
    BINARY_SIZE = "bytes"
    COMPILATION_TIME = "s"

    @override
    def __str__(self) -> str:
        return self.value


@dataclass
class BenchmarkResult:
    name: str
    result: float
    binary_size: int
    output: str = field(repr=False)
    compilation_time: float = field(init=False)
    
    def set_compilation_time(self, compilation_time: float) -> None:
        self.compilation_time = compilation_time

@dataclass
class Benchmark(ABC):
    name: str
    context_path: Path
    unit: BenchmarkUnit
    n_runs: int = field(default=1)
    native_image_args: list[str] = field(default_factory=list)
    benchmark_runner_args: list[str] = field(default_factory=list)
    benchmark_args: list[str] = field(default_factory=list)
    options: ConfigOptions = field(default_factory=ConfigOptions)

    @property
    def log_dir(self) -> Path:
        return self.options.results_output_dir_path / "logs"

    def get_log_path(self, compiler: Compiler, optimization_level: OptimizationLevel | CustomOptimizationLevel) -> Path:
        return self.log_dir / f"{self.name}|{compiler.value}|{optimization_level.label}.log"

    def __post_init__(self):
        self.log_dir.mkdir(exist_ok = True)

    @classmethod
    def from_config(cls, config, options: ConfigOptions) -> "Benchmark":
        benchmark_type = config.get("type")
        if benchmark_type is None:
            raise ValueError("Benchmark type must be specified in the config.")
        if benchmark_type not in ("dacapo", "barista"):
            raise ValueError(f"Unknown benchmark type: {benchmark_type}. Supported types are 'dacapo' and 'barista'.")

        required_fields = ["name"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field '{field}' in benchmark config.")

        config = {k: v for k, v in config.items() if k != "type"}
        from benchmarks.dacapobench import DacapoBenchmark
        from benchmarks.baristabench import BaristaBenchmark

        if options.n_runs is not None:
            config["n_runs"] = options.n_runs

        if options.skip_run:
            config["n_runs"] = 0

        match benchmark_type:
            case "dacapo":
                return DacapoBenchmark(options=options, **config)
            case "barista":
                return BaristaBenchmark(options=options, **config)

    @property
    def binary_path(self) -> Path:
        return self.context_path / self.name

    def _get_binary_size(self):
        if not self.binary_path.exists():
            raise FileNotFoundError(f"Binary does not exist: {self.binary_path}")

        return self.binary_path.stat().st_size

    @abstractmethod
    def run_agent(self, vm_binary: str = "java") -> int:
        pass

    @abstractmethod
    def build_native_image(self, compiler: Compiler, optimization_level: OptimizationLevel = OptimizationLevel.O3, additional_build_args: list[str] | None = None) -> str:
        pass

    def get_prof_file_path(self, compiler: Compiler):
        return (self.context_path / f"{self.name}.iprof").as_posix() if compiler == Compiler.CLOSED else (self.context_path / "profiler-data.json").as_posix()

    def get_dumped_prof_file_path(self, compiler: Compiler):
        return self.options.profiling_data_output_dir_path / f"{self.name}-{compiler.value}.json"

    def build_pgo_optimized_binary(self, compiler: Compiler, additional_build_args: list[str] = []) -> str:
        assert compiler in (Compiler.CLOSED, Compiler.CUSTOM_OPEN), "PGO optimization is only supported for CLOSED and CUSTOM_OPEN compilers."

        prof_file_path = self.get_prof_file_path(compiler)
        profiling_binary_optimization_level = OptimizationLevel.NONE if compiler == Compiler.CLOSED else OptimizationLevel.O0

        if not self.options.skip_profiling:
            # 1. Create instrumented binary
            if not self.options.skip_profiling_build:
                instrumentation_args = ["--pgo-instrument"] if compiler == Compiler.CLOSED else ["-J-DenableInvokeProfilingPhase=true"]
                self.build_native_image(compiler, profiling_binary_optimization_level, instrumentation_args)

            if not self.options.skip_profiling_run:
                # 2. Run the instrumented binary to collect profiling data
                print(f"{C.GRAY}Running benchmark {self.name} to collect profiling data...{C.ENDC}")
                run_args = [f"-XX:ProfilesDumpFile={prof_file_path}"] if compiler == Compiler.CLOSED else []
                self.run(log = True, additional_args = run_args)

        logged_prof_file_path = self.get_dumped_prof_file_path(compiler)

        if self.options.dump_profiling_data:
            prof_file_path = Path(prof_file_path)
            if not prof_file_path.exists():
                raise FileNotFoundError(f"Profiling data file does not exist: {prof_file_path}")
            shutil.copy(prof_file_path, logged_prof_file_path)

        if self.options.use_dumped_profiling_data:
            if not logged_prof_file_path.exists():
                raise FileNotFoundError(f"Dumped profiling data file does not exist: {logged_prof_file_path}")
            prof_file_path = logged_prof_file_path.absolute().as_posix()

        if not self.options.skip_pgo_build:
            # 3. Build the optimized binary using the collected profiling data
            optimized_binary_args = [f"--pgo={prof_file_path}"] if compiler == Compiler.CLOSED else [f"-H:ProfileDataDumpFileName={prof_file_path}", "-J-DenablePGODirectInvokeInlining=true"]
            return self.build_native_image(compiler, OptimizationLevel.NONE, optimized_binary_args + additional_build_args)

        return ""

    @staticmethod
    @abstractmethod
    def _extract_result(output: str) -> float:
        """
        Extract the result from the benchmark output.
        This method should be implemented by subclasses to parse the output
        and return the relevant numeric result.
        """
        pass

    @abstractmethod
    def _get_run_command(self, additional_args: list[str] = []) -> list[str]:
        pass

    def run(self, log: bool = True, additional_args: list[str] = []) -> BenchmarkResult:
        command = self._get_run_command(additional_args)
        output = subprocess.check_output([x for x in command if x], text=True, stderr=subprocess.STDOUT, cwd=self.context_path.as_posix())
        result = BenchmarkResult(self.name, self._extract_result(output), self._get_binary_size(), output)
        if log:
            with open(self.context_path / f"{self.name}.log", "a") as log_file:
                log_file.write(result.output)

        return result


def read_benchmarks_from_file(file_path: Path, options: ConfigOptions) -> dict[str, Benchmark]:
    with open(file_path, "r") as f:
        benchmarks_data = json.load(f) or []

    benchmarks: dict[str, Benchmark] = {}
    for benchmark_config in benchmarks_data:
        benchmark = Benchmark.from_config(benchmark_config, options)
        if benchmark.name in benchmarks:
            raise ValueError(f"Duplicate benchmark name found: {benchmark.name}")
        benchmarks[benchmark.name] = benchmark

    return benchmarks

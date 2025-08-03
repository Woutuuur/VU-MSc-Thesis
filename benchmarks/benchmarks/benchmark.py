from abc import ABC, abstractmethod
from enum import Enum
from numbers import Number
from dataclasses import dataclass, field
from pathlib import Path
import subprocess
from color import Color
from compiler import Compiler
from optimization_level import OptimizationLevel

class BenchmarkUnit(Enum):
    EXECUTION_TIME = "ms"
    THROUGHPUT = "ops/sec"
    BINARY_SIZE = "bytes"

    def __str__(self) -> str:
        return self.value

@dataclass
class BenchmarkResult:
    name: str
    result: float
    binary_size: int
    output: str = field(repr = False)


@dataclass
class Benchmark(ABC):
    name: str
    context_path: Path
    unit: BenchmarkUnit
    n_runs: int = field(default = 1)
    native_image_args: list[str] = field(default_factory = list)
    benchmark_runner_args: list[str] = field(default_factory = list)
    benchmark_args: list[str] = field(default_factory = list)

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
    def build_native_image(self, compiler: Compiler = Compiler.CLOSED, optimization_level = OptimizationLevel.O3, additional_build_args: list[str] = []) -> int:
        pass

    def build_pgo_optimized_binary(self, compiler: Compiler, additional_build_args: list[str] = []) -> None:
        assert compiler in (Compiler.CLOSED, Compiler.CUSTOM_OPEN), "PGO optimization is only supported for CLOSED and CUSTOM_OPEN compilers."

        prof_file_path = (self.context_path / f"{self.name}.iprof").as_posix() if compiler == Compiler.CLOSED else (self.context_path / f"profiler-data.json").as_posix()
        profiling_binary_optimization_level = OptimizationLevel.NONE if compiler == Compiler.CLOSED else OptimizationLevel.O0

        # 1. Create instrumented binary
        instrumentation_args = ["--pgo-instrument"] if compiler == Compiler.CLOSED else []
        self.build_native_image(compiler, profiling_binary_optimization_level, instrumentation_args)
        
        # 2. Run the instrumented binary to collect profiling data
        print(f"{Color.GRAY}Running benchmark {self.name} to collect profiling data...{Color.ENDC}")
        run_args = [f'-XX:ProfilesDumpFile={prof_file_path}'] if compiler == Compiler.CLOSED else []
        self.run(log = False, additional_args = run_args)
        
        # 3. Build the optimized binary using the collected profiling data
        optimized_binary_args = [f"--pgo={prof_file_path}"] if compiler == Compiler.CLOSED else [f"-H:ProfileDataDumpFileName={prof_file_path}", "-J-DdisableVirtualInvokeProfilingPhase=true"]
        self.build_native_image(compiler, OptimizationLevel.NONE, optimized_binary_args + additional_build_args)

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

    def run(self, log = True, additional_args: list[str] = []) -> BenchmarkResult:
        command = self._get_run_command(additional_args)
        output = subprocess.check_output(
            [x for x in command if x],
            text = True,
            stderr = subprocess.STDOUT,
            cwd = self.context_path.as_posix()
        )
        result = BenchmarkResult(
            self.name,
            result = self._extract_result(output),
            binary_size = self._get_binary_size(),
            output = output
        )
        if log:
            with open(self.context_path / f"{self.name}.log", "a") as log_file:
                log_file.write(result.output)

        return result
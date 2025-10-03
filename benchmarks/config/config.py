from collections import defaultdict
import json
from pathlib import Path
from dataclasses import dataclass, field

from benchmarks.benchmark import Benchmark
from benchmarks.compiler import Compiler
from benchmarks.job import BenchmarkJob
from benchmarks.optimization_level import OptimizationLevel
from config.options import ConfigOptions


@dataclass
class Config:
    options: ConfigOptions = field(default_factory=ConfigOptions)
    benchmarks: list[str] = field(default_factory=list)
    optimization_levels_by_compiler: dict[Compiler, list[OptimizationLevel]] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.options, dict):
            self.options = ConfigOptions(**self.options)

    @property
    def compilers(self) -> list[Compiler]:
        return list(self.optimization_levels_by_compiler.keys())

    @classmethod
    def from_file(cls, config_file_path: Path) -> "Config":
        if not config_file_path.exists() or not config_file_path.is_file():
            raise FileNotFoundError(f"Config file '{config_file_path}' does not exist or is not a file.")

        with open(config_file_path, "r") as f:
            return cls(**json.load(f))  # pyright: ignore[reportAny]


    def create_jobs(self, benchmarks: dict[str, "Benchmark"]) -> dict[str, list["BenchmarkJob"]]:
        from benchmarks.job import BenchmarkJob

        jobs: dict[str, list[BenchmarkJob]] = defaultdict(list)

        for benchmark_name in self.benchmarks:
            if benchmark_name not in benchmarks:
                raise ValueError(f"Benchmark '{benchmark_name}' not found in benchmarks.")
            benchmark = benchmarks[benchmark_name]
            for compiler, optimization_levels in self.optimization_levels_by_compiler.items():
                for optimization_level in optimization_levels:
                    job = BenchmarkJob(benchmark=benchmark, optimization_level=optimization_level, compiler=compiler)
                    jobs[benchmark_name].append(job)

        return jobs

    def check_installations(self) -> None:
        required_path_for_compilers = {
            Compiler.CLOSED: self.options.graalvm_home,
            Compiler.OPEN: self.options.graalvm_open_home,
        }

        for compiler in self.compilers:
            if compiler not in required_path_for_compilers:
                continue

            required_path = required_path_for_compilers[compiler]
            if not required_path.exists():
                raise EnvironmentError(f"{compiler.name} path does not exist: {required_path}")
            if not required_path.is_dir():
                raise EnvironmentError(f"{compiler.name} path is not a directory: {required_path}")
            if not (required_path / "bin" / "native-image").exists():
                raise EnvironmentError(f"{compiler.name} does not contain 'bin/native-image': {required_path}")

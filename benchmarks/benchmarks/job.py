from collections import defaultdict
from dataclasses import dataclass, field
import json

from pathlib import Path

from benchmarks.optimization_level import OptimizationLevel
from benchmarks.benchmark import Benchmark
from benchmarks.compiler import Compiler


@dataclass(frozen=True)
class BenchmarkJob:
    benchmark: Benchmark = field(hash=False)
    optimization_level: OptimizationLevel
    compiler: Compiler


def read_jobs_from_config_file(config_file_path: Path, benchmarks: dict[str, Benchmark]) -> dict[str, list[BenchmarkJob]]:
    with open(config_file_path, "r") as f:
        config = json.load(f)

    jobs = defaultdict(list)
    for benchmark_name in config.get("benchmarks", []):
        for compiler, optimization_levels in config.get("optimization_levels_by_compiler", {}).items():
            for optimization_level in optimization_levels:
                jobs[benchmark_name].append(
                    BenchmarkJob(
                        benchmark=benchmarks[benchmark_name],
                        optimization_level=OptimizationLevel[optimization_level],
                        compiler=Compiler[compiler]
                    )
                )

    return jobs

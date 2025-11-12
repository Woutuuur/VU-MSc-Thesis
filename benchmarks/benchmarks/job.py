from dataclasses import dataclass, field
import json

from pathlib import Path
from typing import cast

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
        config = json.load(f)  # pyright: ignore[reportAny]

    return {
        benchmark_name: [
            BenchmarkJob(
                benchmark=benchmarks[benchmark_name],
                optimization_level=OptimizationLevel[optimization_level],
                compiler=Compiler[compiler]
            )
            for compiler, optimization_levels in cast(dict[str, list[str]], config.get("optimization_levels_by_compiler", {})).items()   # pyright: ignore[reportAny]
            for optimization_level in optimization_levels
        ] 
        for benchmark_name in cast(list[str], config.get("benchmarks", []))  # pyright: ignore[reportAny]
    }

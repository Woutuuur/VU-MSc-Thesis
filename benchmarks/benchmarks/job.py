import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from benchmarks.benchmark import Benchmark
from benchmarks.compiler import Compiler
from benchmarks.optimization_level import CustomOptimizationLevel, OptimizationLevel, OptimizationLevelConfig


@dataclass(frozen=True)
class BenchmarkJob:
    benchmark: Benchmark = field(hash=False)
    optimization_level: OptimizationLevel | CustomOptimizationLevel
    compiler: Compiler

def _create_optimization_level_from_config(optimization_level: OptimizationLevelConfig | str):
    if isinstance(optimization_level, str):
        return OptimizationLevel[optimization_level]

    return CustomOptimizationLevel.from_optimization_level_config(optimization_level)

def read_jobs_from_config_file(config_file_path: Path, benchmarks: dict[str, Benchmark]) -> dict[str, list[BenchmarkJob]]:
    with open(config_file_path, "r") as f:
        config = json.load(f)  # pyright: ignore[reportAny]

    return {
        benchmark_name: [
            BenchmarkJob(
                benchmark=benchmarks[benchmark_name],
                optimization_level=_create_optimization_level_from_config(optimization_level),
                compiler=Compiler[compiler]
            )
            for compiler, optimization_levels in cast(dict[str, list[str | OptimizationLevelConfig]], config.get("optimization_levels_by_compiler", {})).items()   # pyright: ignore[reportAny]
            for optimization_level in optimization_levels
        ] 
        for benchmark_name in cast(list[str], config.get("benchmarks", []))  # pyright: ignore[reportAny]
    }

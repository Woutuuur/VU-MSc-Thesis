from pathlib import Path
import json
from typing import TypedDict, cast


class CallSiteProfile(TypedDict):
    receiverCounts: dict[str, int]
    totalCount: int
    isDirectCall: bool
    targetMethod: str


# Counts obtained from https://github.com/dacapobench/dacapobench/tree/main/benchmarks/bms (stats-bytecode.yml files)
invokevirtual_counts = {
    "avrora":     662067610,
    "batik":       35792930,
    "biojava":   2119544767,
    "graphchi":   251040420,
    "h2":        4016442144,
    "sunflow":  10067429660,
    "lusearch":  4030684851,
    "luindex":    700288730,
    "pmd":        448110588,
    "xalan":      773181417
}
invokeinterface_counts = {
    "avrora":     108924353,
    "batik":        9116416,
    "biojava":   1073092693,
    "graphchi":  5254567849,
    "h2":         522522954,
    "sunflow":   2288314686,
    "lusearch":  2225276279,
    "luindex":    232037814,
    "pmd":        688069215,
    "xalan":       77236529
}

COMPILER_NAME = "custom_open"

profiling_data_path = Path("results") / "current" / "profiling-data"
benchmarks = list(invokevirtual_counts.keys())

def profiling_data_path_for_benchmark(benchmark: str) -> Path:
    return profiling_data_path / f"{benchmark}-{COMPILER_NAME}.json"

for benchmark in benchmarks:
    with open(profiling_data_path_for_benchmark(benchmark), "r") as f:
        profiling_data = cast(list[CallSiteProfile], json.load(f))
    total_indirect_calls_count = sum(profile["totalCount"] for profile in profiling_data)
    expected_indirect_calls_count = invokevirtual_counts[benchmark] + invokeinterface_counts[benchmark]
    print(f"{benchmark}:")
    print(f"PGO data: {total_indirect_calls_count:>12}")
    print(f"Expected: {expected_indirect_calls_count:>12}\n")

combined = {
    benchmark: invokevirtual_counts[benchmark] + invokeinterface_counts[benchmark]
    for benchmark in benchmarks
}

print(list(sorted(combined.items(), key=lambda item: item[1], reverse=True)))

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import statistics

def extract_result(output: str) -> float:
    if m := re.search(r".* in (\d+) msec .*", output, re.MULTILINE):
        return float(m.group(1))

    raise ValueError(f"Could not extract execution time from output: {output}")

@dataclass
class BenchmarkResult:
    name: str
    optimization_level: str
    results: list[float]
    
    def average(self) -> float:
        return statistics.mean(self.results)

    def stddev(self) -> float:
        return statistics.stdev(self.results) if len(self.results) > 1 else 0.0

    def median(self) -> float:
        return statistics.median(self.results)

command_args = {
    "lusearch": "-t 16 --no-validation -Dorg.apache.lucene.store.MMapDirectory.enableMemorySegments=false",
    "sunflow": "-t 1",
    "graphchi": "-t 1"
}

benchmark_files = [f for f in Path(".").glob("*") if f.is_file() and not Path(__file__).samefile(f) and not f.name.endswith(".so")]

benchmark_results: list[BenchmarkResult] = []

N_RUNS = 25

for benchmark in benchmark_files:
    name, *_, optimization_level = benchmark.name.split("_")
    if name not in command_args:
        print(f"Skipping {benchmark.name} (no command args defined)")
        continue
    args = command_args[name].split()
    results: list[float] = []
    print("Running", benchmark.name, name, *args)
    for _ in range(N_RUNS):
        output = subprocess.check_output([f"./{benchmark.name}", name, *args], text=True, stderr=subprocess.STDOUT)
        results.append(extract_result(output))
    benchmark_results.append(BenchmarkResult(name, optimization_level, results))

for result in benchmark_results:
    print(f"{result.name:<10} {result.optimization_level:>20}: avg {result.average():>8.2f} msec, stddev {result.stddev():>4.2f} msec, median {result.median():>8.2f} msec")

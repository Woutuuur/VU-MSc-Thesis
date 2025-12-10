import csv
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev, median

from pprint import pprint

import matplotlib
import matplotlib.pyplot as plt

BENCHMARK_ORDER = [
    "avrora",
    "batik",
    "biojava",
    "graphchi",
    "h2",
    "luindex",
    "lusearch",
    "pmd",
    "sunflow",
    "xalan",
    "micronaut-hello-world",
    "micronaut-shopcart",
    "micronaut-similarity",
]

def import_csv_data(filename):
    rows = []
    with open(filename, "r", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row["compilation_time_seconds"] = float(row["compilation_time_seconds"])
            rows.append(row)
    return rows

def compute_speedups(rows):
    benchmark_map = defaultdict(lambda: defaultdict(list))
    
    for row in rows:
        benchmark_map[row["benchmark"]][row["optimization_level"]].append(row["compilation_time_seconds"])

    return {
        benchmark: [o3_time / phase_time for o3_time, phase_time in zip(levels["O3"], levels["Phase skipping O3"])]
        for benchmark, levels in benchmark_map.items()
    }

def create_speedup_plot(rows, filename_suffix):
    speedup_map = compute_speedups(rows)
    
    pprint({name: (mean(speedups), median(speedups), stdev(speedups)) for name, speedups in speedup_map.items()})

    sorted_benchmarks = sorted(speedup_map.keys(), key=BENCHMARK_ORDER.index)
    sorted_speedups = [speedup_map[name] for name in sorted_benchmarks]

    plt.figure(figsize=(len(sorted_benchmarks) * 0.8, 6))
    plt.axhline(1.0, color="gray", linestyle="--", linewidth=1, zorder=0)
    plt.boxplot(sorted_speedups, tick_labels=sorted_benchmarks)
    plt.ylabel("Speedup (O3 / Phase skipping O3)")
    plt.xlabel("Benchmark")
    plt.xticks(rotation=45, ha="right")

    output_dir = Path("results") / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"custom_open_{filename_suffix}.svg"
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved plot: {path}")

def main():
    matplotlib.use("Agg")

    if len(sys.argv) != 2:
        script = Path(sys.argv[0]).name
        print(f"Usage: python {script} <data_file.csv>")
        sys.exit(1)

    rows = import_csv_data(sys.argv[1])
    create_speedup_plot(rows, f"all_compilation_speedup")

if __name__ == "__main__":
    main()

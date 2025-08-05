import csv
import sys
import matplotlib
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f"]
PATTERNS = ["", "/", ".", "\\", "*", "\\//\\", "-", "\\"]
EXECUTION_TIME_BENCHMARKS = ["avrora", "batik", "biojava", "graphchi", "h2", "luindex", "luseach", "pmd", "sunflow", "xalan"]
THROUGHPUT_BENCHMARKS = ["micronaut-hello-world", "micronaut-shopcart", "micronaut-similarity"]


def import_csv_data(filename: str) -> pd.DataFrame:
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            row["result"] = float(row["result"])
            row["binary_size"] = float(row["binary_size"])
            data.append(row)
    return pd.DataFrame(data)


def calculate_speedup(df: pd.DataFrame, inverse: bool = False) -> pd.DataFrame:
    result = []
    for benchmark in df["benchmark"].unique():
        bench_data = df[df["benchmark"] == benchmark]
        baseline_mean = bench_data[bench_data["optimization_level"] == "-O0"]["result"].mean()

        for _, row in bench_data.iterrows():
            speedup = row["result"] / baseline_mean if inverse else baseline_mean / row["result"]
            result.append({"benchmark": benchmark, "optimization_level": row["optimization_level"], "result": speedup, "binary_size": row["binary_size"]})

    return pd.DataFrame(result)


def aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["benchmark", "optimization_level"]).agg({"result": ["mean", "std"], "binary_size": "mean"}).round(2)


def plot_benchmarks(data: pd.DataFrame, title: str, ylabel: str, plot_type: str):
    ax = plt.gca()
    ax_twin = ax.twinx()

    benchmarks = sorted(data.index.get_level_values("benchmark").unique())
    optimization_levels = sorted(data.index.get_level_values("optimization_level").unique())

    x_positions = range(len(benchmarks))
    bar_width = 0.8 / len(optimization_levels)

    for i, optimization_level in enumerate(optimization_levels):
        y_values = []
        errors = []
        binary_sizes = []

        for benchmark in benchmarks:
            row = data.loc[(benchmark, optimization_level)]
            y_values.append(row[("result", "mean")])
            errors.append(row[("result", "std")])
            binary_sizes.append(row[("binary_size", "mean")])

        offset = (i - len(optimization_levels) / 2) * bar_width + bar_width / 2
        bar_positions = [x + offset for x in x_positions]

        metric_bar_positions = [p - bar_width / 4 for p in bar_positions]
        binary_bar_positions = [p + bar_width / 4 for p in bar_positions]

        ax.bar(metric_bar_positions, y_values, bar_width / 2, label=optimization_level, color=COLORS[i], alpha=0.8, hatch=PATTERNS[i] * 2, hatch_linewidth=0.25)
        ax_twin.bar(binary_bar_positions, binary_sizes, bar_width / 2, color=COLORS[i], alpha=0.4, hatch=PATTERNS[i] * 2, hatch_linewidth=0.25)
        ax.errorbar(metric_bar_positions, y_values, yerr=errors, fmt="none", color="black", capsize=3, alpha=0.7)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(benchmarks, rotation=0)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, axis="y", alpha=0.3)

    ax_twin.set_ylabel("Binary Size (bytes)", color="grey")
    ax_twin.tick_params(axis="y", labelcolor="grey")

    if plot_type == "speedup":
        ax.axhline(y=1.0, color="black", linestyle="--", alpha=0.5)


def create_plot(execution_data: pd.DataFrame, throughput_data: pd.DataFrame, compiler: str, plot_type: str):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

    plt.sca(ax1)
    ylabel = "Execution Time (ms)" if plot_type == "absolute" else "Speedup vs -O0"
    plot_benchmarks(execution_data, "Execution Time Benchmarks", ylabel, plot_type)

    plt.sca(ax2)
    ylabel = "Throughput (ops/sec)" if plot_type == "absolute" else "Speedup vs -O0"
    plot_benchmarks(throughput_data, "Throughput Benchmarks", ylabel, plot_type)

    handles = []
    optimization_levels = sorted(execution_data.index.get_level_values("optimization_level").unique())
    for i, label in enumerate(optimization_levels):
        handles.append(Patch(facecolor=COLORS[i], hatch=PATTERNS[i] * 3, label=label))
    handles.append(Patch(facecolor="lightgrey", label="Binary Size"))

    fig.legend(handles=handles, title="Optimization Level", loc="lower center", ncol=len(handles))
    fig.suptitle(f'Benchmark results for {compiler.replace("_", " ").lower()} compiler', fontsize=16)

    plt.tight_layout(rect=(0, 0.1, 1, 1))

    (Path("results") / "plots").mkdir(exist_ok=True, parents=True)
    plt.savefig(f"results/plots/{plot_type}_{compiler.lower()}.png", dpi=300, bbox_inches="tight")
    plt.close()


def main():
    matplotlib.use("Agg")

    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <data_file.csv>")
        sys.exit(1)

    df = import_csv_data(sys.argv[1])

    for compiler in df["compiler"].unique():
        compiler_data = df[df["compiler"] == compiler]

        execution_raw = compiler_data[compiler_data["benchmark"].isin(EXECUTION_TIME_BENCHMARKS)]
        throughput_raw = compiler_data[compiler_data["benchmark"].isin(THROUGHPUT_BENCHMARKS)]

        execution_absolute = aggregate_data(execution_raw)
        throughput_absolute = aggregate_data(throughput_raw)

        execution_speedup = aggregate_data(calculate_speedup(execution_raw, inverse=False))
        throughput_speedup = aggregate_data(calculate_speedup(throughput_raw, inverse=True))

        create_plot(execution_absolute, throughput_absolute, compiler, "absolute")
        create_plot(execution_speedup, throughput_speedup, compiler, "speedup")


if __name__ == "__main__":
    main()

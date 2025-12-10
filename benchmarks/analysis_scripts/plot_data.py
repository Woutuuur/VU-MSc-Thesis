import sys
import math
import matplotlib
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

COLORS = [
    "#aec7e8",
    "#ffbb78",
    "#98df8a",
    "#ff9896",
    "#c5b0d5",
    "#c49c94",
    "#f7b6d2",
    "#dbdb8d"
]

PATTERNS = ["", "/", ".", "\\", "*", "\\//\\", "-", "||"]

EXECUTION_TIME_BENCHMARKS = ["avrora", "batik", "biojava", "graphchi", "h2", "luindex", "lusearch", "pmd", "sunflow", "xalan"]
THROUGHPUT_BENCHMARKS = ["micronaut-hello-world", "micronaut-shopcart", "micronaut-similarity"]

def import_csv_data(filename):
    df = pd.read_csv(filename)
    df["result"] = df["result"].astype(float)
    df["binary_size"] = df["binary_size"].astype(float)
    return df

def calculate_normalized_metrics(df):
    is_throughput = df['benchmark'].isin(THROUGHPUT_BENCHMARKS)

    baseline_o0 = df[df['optimization_level'] == 'O0'].groupby('benchmark').agg(
        baseline_result_mean=('result', 'mean'),
        baseline_size_mean=('binary_size', 'mean')
    )

    baseline_o3 = df[df['optimization_level'] == 'O3'].groupby('benchmark').agg(
        baseline_o3_result_mean=('result', 'mean'),
        baseline_o3_size_mean=('binary_size', 'mean')
    )

    df = pd.merge(df, baseline_o0, on='benchmark', how='left')
    df = pd.merge(df, baseline_o3, on='benchmark', how='left')

    df['speedup'] = np.where(is_throughput, df['result'] / df['baseline_result_mean'], df['baseline_result_mean'] / df['result'])
    df['speedup_o3'] = np.where(is_throughput, df['result'] / df['baseline_o3_result_mean'], df['baseline_o3_result_mean'] / df['result'])
    df['norm_binary_size'] = df['binary_size'] / df['baseline_size_mean']
    df['norm_binary_size_o3'] = df['binary_size'] / df['baseline_o3_size_mean']
    
    return df

def aggregate_data(df):
    return df.groupby(["benchmark", "optimization_level"]).agg({
        "speedup": ["mean", "std"],
        "speedup_o3": ["mean", "std"],
        "norm_binary_size": ["mean", "std"],
        "norm_binary_size_o3": ["mean", "std"]
    }).round(2)

def plot_metric_on_ax(ax, data, benchmarks, metric_col, y_label):
    optimization_levels = sorted(data.index.get_level_values("optimization_level").unique())
    bar_width = 0.8 / len(optimization_levels)

    for i, level in enumerate(optimization_levels):
        rows = data.xs(level, level="optimization_level")[metric_col].loc[benchmarks]
        offset = (i - len(optimization_levels) / 2) * bar_width + bar_width / 2
        positions = [x + offset for x in range(len(benchmarks))]

        ax.bar(
            positions,
            rows["mean"],
            bar_width,
            label=level,
            color=COLORS[i % len(COLORS)],
            alpha=0.9,
            edgecolor="black",
            linewidth=0.5,
            hatch=PATTERNS[i % len(PATTERNS)] * 2
        )

        ax.errorbar(positions, rows["mean"], yerr= rows["std"], fmt="none", color="black", capsize=2, alpha=0.8, lw=1)

    ax.set_xticks(range(len(benchmarks)))
    ax.set_xticklabels(benchmarks, rotation=0, fontsize=11)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")
    ax.axhline(y=1.0, color="black", linestyle="--", alpha=0.6, linewidth=1.2)

def create_single_metric_plot(data, compiler, metric_col, y_label, filename_suffix, benchmarks_list):
    available_benchmarks = sorted([b for b in benchmarks_list if b in data.index.get_level_values("benchmark").unique()])
    
    num_benchmarks = len(available_benchmarks)
    
    if num_benchmarks > 5:
        nrows = 2
        figsize = (12, 10)
        mid_point = math.ceil(num_benchmarks / 2)
        bench_batches = [available_benchmarks[:mid_point], available_benchmarks[mid_point:]]
        bottom_margin = 0.12 
    else:
        nrows = 1
        figsize = (12, 6)
        bench_batches = [available_benchmarks]
        bottom_margin = 0.22 

    fig, axes = plt.subplots(nrows, 1, figsize=figsize, sharey=False)
    
    if nrows == 1:
        axes = [axes]

    for ax, batch in zip(axes, bench_batches):
        plot_metric_on_ax(ax, data, batch, metric_col, y_label)

    handles = []
    optimization_levels = sorted(data.index.get_level_values("optimization_level").unique())
    for i, label in enumerate(optimization_levels):
        legend_hatch = PATTERNS[i % len(PATTERNS)] * 2
        handles.append(Patch(facecolor=COLORS[i % len(COLORS)], hatch=legend_hatch, label=label, edgecolor='black'))

    ncols = math.ceil(len(handles) / 2)

    fig.legend(
        handles=handles, 
        title="Optimization Level", 
        loc="lower center", 
        ncol=ncols,
        bbox_to_anchor=(0.5, 0.02),
        handleheight=2,
        handlelength=3,
        fontsize=11,
        title_fontsize=12
    )
    
    plt.tight_layout(rect=(0, bottom_margin, 1, 1))

    output_dir = Path("results") / "plots"
    output_dir.mkdir(exist_ok=True, parents=True)
    filename = f"results/plots/{compiler.lower()}_{filename_suffix}.svg"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    print(f"Saved plot: {filename}")
    plt.close()

def process_benchmark_set(df, compiler, benchmarks, suite_name):
    suite_data = df[df["benchmark"].isin(benchmarks)].copy()

    processed_data = calculate_normalized_metrics(suite_data)
    aggregated = aggregate_data(processed_data)
    
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(aggregated)

    create_single_metric_plot(
        aggregated, 
        compiler, 
        metric_col="speedup", 
        y_label="Speedup (higher is better)", 
        filename_suffix=f"{suite_name.lower()}_speedup",
        benchmarks_list=benchmarks
    )

    create_single_metric_plot(
        aggregated, 
        compiler, 
        metric_col="norm_binary_size", 
        y_label="Normalized size (lower is better)", 
        filename_suffix=f"{suite_name.lower()}_binary_size",
        benchmarks_list=benchmarks
    )

    return processed_data

def main():
    matplotlib.use("Agg")

    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <data_file.csv>")
        sys.exit(1)

    df = import_csv_data(sys.argv[1])

    for compiler in df["compiler"].unique():
        data = df[df["compiler"] == compiler]
        dacapo_processed = process_benchmark_set(data, compiler, EXECUTION_TIME_BENCHMARKS, "Dacapo")
        barista_processed = process_benchmark_set(data, compiler, THROUGHPUT_BENCHMARKS, "Barista")

        combined_processed = pd.concat([dacapo_processed, barista_processed], ignore_index=True)
        combined_aggregated = aggregate_data(combined_processed)

        avg_speedup_o3 = combined_aggregated.groupby(level='optimization_level')['speedup_o3'].agg(['mean', 'std']).round(2)
        avg_norm_binary_size_o3 = combined_aggregated.groupby(level='optimization_level')['norm_binary_size_o3'].agg(['mean', 'std']).round(2)

        print(f"\nAverage speedup vs O3 across all benchmarks:")
        print(avg_speedup_o3)

        print(f"\nAverage binary size increase vs O3 across all benchmarks (normalized):")
        print(avg_norm_binary_size_o3)

if __name__ == "__main__":
    main()

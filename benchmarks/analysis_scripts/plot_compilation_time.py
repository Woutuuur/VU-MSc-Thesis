import sys
import math
import matplotlib
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

COLORS = [
    "#aec7e8", # Blue
    "#ffbb78", # Orange
    "#98df8a", # Green
    "#ff9896", # Red
    "#c5b0d5", # Purple
    "#c49c94", # Brown
    "#f7b6d2", # Pink
    "#dbdb8d"  # Yellow
]

PATTERNS = ["", "/", ".", "\\", "*", "\\//\\", "-", "||"]
BENCHMARKS = ["avrora", "batik", "biojava", "graphchi", "h2", "luindex", "lusearch", "pmd", "sunflow", "xalan", "micronaut-hello-world", "micronaut-shopcart", "micronaut-similarity"]

def import_csv_data(filename):
    df = pd.read_csv(filename)
    df["compilation_time_seconds"] = df["compilation_time_seconds"].astype(float)
    return df

def aggregate_data(df):
    return df.groupby(["benchmark", "optimization_level"]).agg({
        "compilation_time_seconds": ["mean", "std"],
    }).round(2)

def plot_metric_on_ax(ax, data, benchmarks, metric_col, y_label):
    optimization_levels = sorted(data.index.get_level_values("optimization_level").unique())
    bar_width = 0.8 / len(optimization_levels)

    for i, level in enumerate(optimization_levels):
        rows = data.xs(level, level="optimization_level")[metric_col].loc[benchmarks]
        standard_errors = rows["std"].fillna(0)
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

        ax.errorbar(positions, rows["mean"], yerr=standard_errors, fmt="none", color="black", capsize=2, alpha=0.8, lw=1)

    ax.set_xticks(range(len(benchmarks)))
    ax.set_xticklabels(benchmarks, rotation=0, fontsize=11)
    ax.set_ylabel(y_label, fontsize=12)
    ax.grid(True, axis="y", alpha=0.3, linestyle="--")


def create_single_metric_plot(data, compiler, metric_col, y_label, filename_suffix, benchmarks_list):
    benchmarks = sorted(b for b in benchmarks_list if b in data.index.get_level_values("benchmark").unique())

    if len(benchmarks) > 5:
        mid = math.ceil(len(benchmarks) / 2)
        batches = [benchmarks[:mid], benchmarks[mid:]]
        figsize = (12, 10)
        bottom = 0.12
    else:
        batches = [benchmarks]
        figsize = (12, 6)
        bottom = 0.22

    fig, axes = plt.subplots(len(batches), 1, figsize=figsize, sharey=False)
    if len(batches) == 1:
        axes = [axes]

    for ax, batch in zip(axes, batches):
        plot_metric_on_ax(ax, data, batch, metric_col, y_label)

    handles = []
    levels = sorted(data.index.get_level_values("optimization_level").unique())
    for i, label in enumerate(levels):
        handles.append(Patch(facecolor=COLORS[i % len(COLORS)], hatch=PATTERNS[i % len(PATTERNS)] * 2, label=label, edgecolor="black"))

    fig.legend(
        handles=handles,
        title="Optimization Level",
        loc="lower center",
        ncol=math.ceil(len(handles) / 2),
        bbox_to_anchor=(0.5, 0.02),
        handleheight=2,
        handlelength=3,
        fontsize=11,
        title_fontsize=12
    )

    plt.tight_layout(rect=(0, bottom, 1, 1))

    output_dir = Path("results/plots")
    output_dir.mkdir(exist_ok=True, parents=True)
    filename = output_dir / f"{compiler.lower()}_{filename_suffix}.svg"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    print(f"Saved plot: {filename}")
    plt.close()

def main():
    matplotlib.use("Agg")

    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <data_file.csv>")
        sys.exit(1)

    df = import_csv_data(sys.argv[1])

    for compiler in df["compiler"].unique():
        compiler_data = df[df["compiler"] == compiler]
        aggregated = aggregate_data(compiler_data[["benchmark", "optimization_level", "compilation_time_seconds"]])

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(aggregated)
    
        create_single_metric_plot(
            aggregated, 
            compiler, 
            metric_col="compilation_time_seconds", 
            y_label="Compilation time [s] (lower is better)", 
            filename_suffix=f"all_compilation_time",
            benchmarks_list=BENCHMARKS
        )

if __name__ == "__main__":
    main()

# Experiment runner suite

## Setup

Create and activate the environment and install dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Data analysis and plot generation

Below we detail which commands were used to obtain the data for every figure and table in the thesis. Plots are written as svg files to [results/plots]().

The scripts are located in the [analysis-scripts]() directory. Scripts that were used throughout the study for preliminary analysis but were not used to create the final data in the paper are included in [analysis-scripts/misc]().

### DII

**Figure 3: "DII: Execution time speedup relative to the baseline (O0) for DaCapo benchmarks"**

**Figure 4: "DII: Throughput improvement relative to the baseline (O0) for Barista benchmarks"**

```bash
python3 analysis_scripts/plot_data.py results/DII/results.csv
```

**Table 4: "DII: Binary sizes of generated binaries in MiB"**

```bash
python3 analysis_scripts/binary_sizes_to_typst_table.py results/DII/results.csv
```

**Table 5: "Direct and indirect call site and invocation counts in top 40% of profiling data"**

```bash
python3 analysis_scripts/extract-profile-counts.py
```

**Table 6: "Mean speedup and binary size increase by applying “DII O3 combined” compared to O3 baseline, by benchmark"**

```bash
python3 analysis_scripts/plot_data.py results/DII/results.csv # See stdout
```

**Figure 5: "DII: Compilation times by benchmark and optimization level"**

```bash
python3 analysis_scripts/plot_compilation_time.py results/DII/compilation_results.csv
```

**Table 7: "DII: Mean compilation time"**

```bash
python3 analysis_scripts/compilation_time.py results/DII/
```

### IC

**Figure 6: "IC: Execution time speedup relative to the baseline (O0) for DaCapo and Barista benchmarks"**

```bash
python3 analysis_scripts/plot_data_ic.py results/IC/results.csv
```

**Table 8: "IC: Mean compilation time"**

```bash
python3 analysis_scripts/compilation_time_ic.py results/IC/
```

### IC + DII

**Figure 7: "IC + DII combined: Execution time speedup relative to the baseline (O0) for DaCapo and Barista benchmarks"**

```bash
python3 analysis_scripts/plot_data_ic.py results/IC+DII/results.csv
```

**Table 9: "IC + DII: Binary sizes of generated binaries in MiB"**

```bash
python3 analysis_scripts/binary_sizes_to_typst_table_ic-dii.py results/IC+DII/results-with-dii.csv
```

**Table 10: "IC + DII: Mean compilation time"**

```bash
python3 analysis_scripts/compilation_time_ic-dii.py results/IC+DII/
```

### Phase skipping plots and data

**Figure 8: "Compilation time speedup by applying phase skipping on O3, by benchmark"**

```bash
python3 analysis_scripts/plot_compilation_time_boxplot.py results/phase-skipping/compilation_results.csv
```

**Table 11: "Number of phases considered and skipped on O3, by benchmark"**

```bash
python3 analysis_scripts/phase_skipping_results_to_typst_table.py results/phase-skipping/compilation_results.csv
```

import sys
from pathlib import Path

import pandas as pd

if len(sys.argv) != 2:
    sys.exit(f"usage: python {sys.argv[0]} <data_dir>")

data_dir = Path(sys.argv[1])
csv_path = data_dir / "compilation_results-with-dii.csv"

df = pd.read_csv(csv_path)

required = ["benchmark", "optimization_level", "compilation_time_seconds"]

levels = ["DII O0 combined", "IC + DII O0 combined", "DII O3 combined", "IC + DII O3 combined"]
df = df[df["optimization_level"].isin(levels)]

df["compilation_time_seconds"] = pd.to_numeric(df["compilation_time_seconds"], errors="coerce")

for benchmark in df["benchmark"].unique():
    sub = df[df["benchmark"] == benchmark]

    dii_o0_base = sub[sub["optimization_level"] == "DII O0 combined"]["compilation_time_seconds"].mean()
    dii_o0_with_ic = sub[sub["optimization_level"] == "IC + DII O0 combined"]["compilation_time_seconds"].mean()
    dii_o3_base = sub[sub["optimization_level"] == "DII O3 combined"]["compilation_time_seconds"].mean()
    dii_o3_with_ic = sub[sub["optimization_level"] == "IC + DII O3 combined"]["compilation_time_seconds"].mean()

    o3_pct = (dii_o3_with_ic - dii_o3_base) / dii_o3_base * 100
    o0_pct = (dii_o0_with_ic - dii_o0_base) / dii_o0_base * 100

    print(f"`{benchmark}`, [${dii_o0_base:.2f}$s], [${dii_o0_with_ic:.2f}$s], $(+{o0_pct:.2f}%)$, [${dii_o3_base:.2f}$s], [${dii_o3_with_ic:.2f}$s], $(+{o3_pct:.2f}%)$,")

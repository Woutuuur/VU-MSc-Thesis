import sys
from pathlib import Path

import pandas as pd

if len(sys.argv) != 2:
    sys.exit(f"usage: python {sys.argv[0]} <data_dir>")

data_dir = Path(sys.argv[1])
csv_path = data_dir / "compilation_results.csv"

df = pd.read_csv(csv_path)

required = ["benchmark", "optimization_level", "compilation_time_seconds"]

levels = ["O3", "IC O3", "O0", "IC O0"]
df = df[df["optimization_level"].isin(levels)]

df["compilation_time_seconds"] = pd.to_numeric(df["compilation_time_seconds"], errors="coerce")

for benchmark in df["benchmark"].unique():
    sub = df[df["benchmark"] == benchmark]

    o0_base = sub[sub["optimization_level"] == "O0"]["compilation_time_seconds"].mean()
    o0_dii = sub[sub["optimization_level"] == "IC O0"]["compilation_time_seconds"].mean()
    o3_base = sub[sub["optimization_level"] == "O3"]["compilation_time_seconds"].mean()
    o3_dii = sub[sub["optimization_level"] == "IC O3"]["compilation_time_seconds"].mean()

    o3_delta = o3_dii - o3_base
    o3_pct = o3_delta / o3_base * 100
    o3_text = f"{o3_delta:+.3f}s ({o3_pct:+.2f}%)"

    o0_delta = o0_dii - o0_base
    o0_pct = (o0_delta) / o0_base * 100
    o0_text = f"{o0_delta:+.3f}s ({o0_pct:+.2f}%)"

    print(f"`{benchmark}`, [${o0_base:.2f}$s], [${o0_dii:.2f}$s], $(+{o0_pct:.2f}%)$, [${o3_base:.2f}$s], [${o3_dii:.2f}$s], $(+{o3_pct:.2f}%)$,")

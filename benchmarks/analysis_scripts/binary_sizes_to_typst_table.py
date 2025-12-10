import sys
from collections import defaultdict
import csv
import pandas as pd

def import_csv_data(filename: str) -> pd.DataFrame:
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            row["binary_size"] = int(row["binary_size"])
            data.append(row)
    return pd.DataFrame(data)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <data_file.csv>")
        sys.exit(1)

    df = import_csv_data(sys.argv[1])
    tab = []
    for optimization_level in ["Os", "O0", "O3", "DII O0", "DII O0 combined", "DII O3", "DII O3 combined"]:
        res = [f"[{optimization_level:<15}]"]
        for benchmark in df["benchmark"].unique():
            subset = df[(df["optimization_level"] == optimization_level) & (df["benchmark"] == benchmark)]
            res.append(f'${subset.iloc[0]["binary_size"] / 1000 / 1000:>6.2f}$')
        tab.append(",".join(res))
    print(',\n'.join(tab))

    for benchmark in df["benchmark"].unique():
        subset = df[df["benchmark"] == benchmark]
        o3_size = subset[subset["optimization_level"] == "O3"].iloc[0]["binary_size"]
        o3_dii_size = subset[subset["optimization_level"] == "DII O3 combined"].iloc[0]["binary_size"]
        print(f"{benchmark} CI + DII O3 size increase compared to DII O3: {(o3_dii_size - o3_size) / o3_size * 100:.2f}%")

if __name__ == "__main__":
     main()

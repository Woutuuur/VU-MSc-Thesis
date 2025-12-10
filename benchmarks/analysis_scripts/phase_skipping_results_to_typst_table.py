import csv
import sys
import pandas as pd

def import_csv_data(filename: str) -> pd.DataFrame:
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        data = []
        for row in reader:
            row["phases_skipped"] = int(row["phases_skipped"])
            row["phases_total"] = int(row["phases_total"])
            data.append(row)
    return pd.DataFrame(data)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <data_file.csv>")
        sys.exit(1)

    df = import_csv_data(sys.argv[1])
    tab = []
    for benchmark in df["benchmark"].unique():
        benchmark_str = f"[`{benchmark}`]"
        res = [f"{benchmark_str:<25}"]
        subset = df[(df["optimization_level"] == "Phase skipping O3") & (df["benchmark"] == benchmark)]
        skipped, total = subset.iloc[0]["phases_skipped"], subset.iloc[0]["phases_total"]
        percentage_skipped = (skipped / total) * 100
        res.append(f'${total:>7}$')
        res.append(f'[${skipped:>6}$  (${percentage_skipped:>5.2f}%$)]')
        tab.append(",".join(res))
    print(',\n'.join(tab) + ',')

if __name__ == "__main__":
     main()

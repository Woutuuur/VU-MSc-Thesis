import json
import pandas as pd 
from pathlib import Path

profile_data_dir = Path("results/current/profiling-data")
files = list(profile_data_dir.glob("*.json"))

def proportion_virtual_in_top_n_percent(call_sites: pd.DataFrame, n_percent: float) -> float:
    n = int(len(call_sites) * n_percent / 100)
    top_n = call_sites.nlargest(n, "totalCount")
    virtual_counts = top_n["totalCount"].where(~top_n["isDirectCall"]).sum()
    total_counts = top_n["totalCount"].sum()

    return virtual_counts / total_counts

def proportion_of_total_count_in_top_n_percent(call_sites: pd.DataFrame, n_percent: float) -> float:
    n = int(len(call_sites) * n_percent / 100)
    top_n = call_sites.nlargest(n, "totalCount")

    return top_n["totalCount"].sum() / call_sites["totalCount"].sum()

def data_analysis(call_sites: pd.DataFrame) -> pd.DataFrame:
    call_sites.sort_values(by="totalCount", ascending=False).reset_index(drop=True)

    total_counts = call_sites["totalCount"].values
    virtual_counts = call_sites["totalCount"].where(~call_sites["isDirectCall"], 0).values

    total_callsites = len(total_counts)
    total_virtual_callsites = len(call_sites[call_sites["isDirectCall"] == False])

    total_virtual_calls = sum(virtual_counts)
    total_calls_count = sum(total_counts)

    virtual_calls_proportion = total_virtual_calls / total_calls_count
    virtual_callsite_proportion = total_virtual_callsites / total_callsites

    res = pd.DataFrame({
        "total_callsites": total_callsites,
        "total_virtual_callsites": total_virtual_callsites,
        "total_virtual_calls": total_virtual_calls,
        "total_calls_count": total_calls_count,
        "virtual_calls_proportion": virtual_calls_proportion,
        "virtual_callsite_proportion": virtual_callsite_proportion
    }, index=[0])

    for percent in [1, 2, 3, 4, 10]:
        res[f"prop_virtual_top_{percent}%"] = proportion_virtual_in_top_n_percent(call_sites, percent)

    for percent in [1, 2, 3, 4, 10]:
        res[f"prop_of_total_top_{percent}%"] = proportion_of_total_count_in_top_n_percent(call_sites, percent)

    return res

all_data = []
for file in files:
    with open(file, "r") as f:
        data = json.load(f)

    all_data.extend(data)

all_data = pd.DataFrame(all_data)
all_data = all_data.sort_values(by="totalCount", ascending=False).reset_index(drop=True)
pd.set_option('display.float_format', '{:.4f}'.format)
print(data_analysis(all_data).T)

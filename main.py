from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
import json

# ─────────────────────────────
# PATHS
# ─────────────────────────────
ROOT = Path.cwd()
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

YEARS = ["2018_19", "2019_20", "2020_21", "2021_22"]

# ─────────────────────────────
# LOAD ASI BLOCKS
# ─────────────────────────────
def load_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    # Explicitly exclude 'YR', 'BLK', and 'Unnamed' columns to prevent collisions
    df = pd.read_csv(path, nrows=0)
    exclude = {'YR', 'BLK'}
    cols = [c for c in df.columns if c.upper() not in exclude and not c.startswith('Unnamed')]
    df = pd.read_csv(path, usecols=cols)
    df.columns = df.columns.str.strip().str.upper()
    return df

def get_id_col(df):
    # Priority ID columns for ASI data blocks
    for c in ["DSL", "AJ01", "AH01", "ID"]:
        if c in df.columns:
            return c
    # Fallback to the first column if none match
    return df.columns[0]

def load_year(year_str):
    suf = year_str.replace('_', '')
    year_folder = DATA_DIR / f"ASI_DATA_{year_str}_CSV"
    
    # Load blocks A (General), J (Output), H (Input/Labor)
    A = load_csv(year_folder / f"blkA{suf}.csv")
    J = load_csv(year_folder / f"blkJ{suf}.csv")
    H = load_csv(year_folder / f"blkH{suf}.csv")

    id_a, id_j, id_h = get_id_col(A), get_id_col(J), get_id_col(H)
    
    # Cast IDs to string to ensure safe merging
    for d, k in [(A, id_a), (J, id_j), (H, id_h)]:
        d[k] = d[k].astype(str).str.strip()

    # Merge on the specific ID column found in each block
    df = A.merge(J, left_on=id_a, right_on=id_j, suffixes=('', '_j'))
    df = df.merge(H, left_on=id_a, right_on=id_h, suffixes=('', '_h'))

    # Map standardized columns
    col_map = {id_a: "id"}
    if "A5" in df.columns: col_map["A5"] = "nic"
    if "MULT" in df.columns: col_map["MULT"] = "weight"
    if "J113" in df.columns: col_map["J113"] = "gva"
    if "H14" in df.columns: col_map["H14"] = "workers"

    df = df.rename(columns=col_map)
    needed = ["id", "nic", "weight", "gva", "workers"]
    
    # Ensure all needed columns exist, fill with 0 if missing
    for c in needed:
        if c not in df.columns:
            df[c] = 0
            
    df = df[needed].copy()
    df["year"] = int(year_str.split("_")[0]) + 1
    return df

# ─────────────────────────────
# PIPELINE
# ─────────────────────────────
def main():
    print("Starting Pipeline...")
    dfs = []
    for y in YEARS:
        print(f"Processing {y}...")
        try:
            dfs.append(load_year(y))
        except Exception as e:
            print(f"  Error on {y}: {e}")

    if not dfs:
        print("No data available for analysis.")
        return

    df = pd.concat(dfs, ignore_index=True)
    df["industry"] = df["nic"].astype(str).str.strip().str[:2]

    # Convert columns to numeric
    for c in ["gva", "weight"]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        
    df["wgva"] = df["gva"] * df["weight"]
    agg = df.groupby(["industry", "year"])["wgva"].sum().reset_index()
    pivot = agg.pivot(index="industry", columns="year", values="wgva")
    
    metrics = {}
    years_present = pivot.columns.tolist()
    # Simple average GVA growth/drop calculation between consecutive years
    if 2020 in years_present and 2021 in years_present:
        # (GVA_2021 - GVA_2020) / GVA_2020
        change = ((pivot[2021] - pivot[2020]) / pivot[2020].replace(0, np.nan) * 100)
        metrics["avg_gva_drop_pct"] = float(change.mean())

    print("\nRESULTS:")
    print(metrics)
    with open(OUTPUTS_DIR / "primary_metric.json", "w") as f:
        json.dump(metrics, f, indent=4)
    print(f"Metrics saved to {OUTPUTS_DIR}")

if __name__ == "__main__":
    main()

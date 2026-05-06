from pathlib import Path
import pandas as pd
import numpy as np
import json
import traceback
import zipfile # Added import
import matplotlib.pyplot as plt # Added import
import seaborn as sns # Added import

ROOT = Path.cwd() # This is /content/ in Colab
DATA_DIR = ROOT # Set DATA_DIR to /content/ as files are directly there
OUTPUTS_DIR = ROOT / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Corrected filenames based on available files
FILES = {
    "2018_19": "ASI_DATA_2018_19_CSV.zip",
    "2019_20": "ASI_DATA_2019_20_CSV.zip",
    "2020_21": "ASI_DATA_2020_21_CSV.zip",
    "2021_22": "ASI_DATA_2021_22_CSV.zip",
}

# ─────────────────────────────
# HELPER for ZIP files
# ─────────────────────────────
def find_file_in_zip(zfile, keyword):
    """Finds a file within a zip file whose name contains the keyword."""
    for name in zfile.namelist():
        if keyword.lower() in name.lower():
            return name
    raise Exception(f"{keyword} file not found in zip")

# ─────────────────────────────
# LOAD CSV
# ─────────────────────────────
def load_csv(file_obj):
    """Loads a CSV from a file-like object and cleans column names."""
    df = pd.read_csv(file_obj)
    df.columns = df.columns.str.strip().str.upper()
    return df

def infer_year(year_key):
    """Infers the year from a year_key string (e.g., '2018_19' -> 2019)."""
    for y in ["2018", "2019", "2020", "2021", "2022"]:
        if y in year_key:
            # Assuming year_key like 'YYYY_YY' refers to ending year
            return int(y.split("_")[0]) + 1 # e.g. 2018_19 means year 2019 data
    return None

def get_best_id_col(df, block_name, year_key):
    """Identifies the most suitable ID column for a given dataframe block."""
    candidate_cols = []
    if block_name == 'A':
        candidate_cols = ["A1", "DSL", "AH01", "ID"] # 'A1' is a common factory ID for block A
    else: # For J and H blocks, 'AJ01' is typically the common ID
        candidate_cols = ["AJ01", "DSL", "AH01", "ID"]

    for c in candidate_cols:
        if c in df.columns:
            return c
    raise ValueError(f"No suitable ID column found for block {block_name} in {year_key}. Available columns: {df.columns.tolist()}")


def load_year(year_key, filename):
    """Loads and merges data for a specific year from a zip file."""
    print(f"Loading {year_key} data from {filename}...")
    path = DATA_DIR / filename

    with zipfile.ZipFile(path) as z:
        A = load_csv(z.open(find_file_in_zip(z, "blkA")))
        J = load_csv(z.open(find_file_in_zip(z, "blkJ")))
        H = load_csv(z.open(find_file_in_zip(z, "blkH")))

    # Determine ID columns for each block dynamically
    id_a_col = get_best_id_col(A, 'A', year_key)
    id_j_col = get_best_id_col(J, 'J', year_key)
    id_h_col = get_best_id_col(H, 'H', year_key)

    # Ensure ID columns are string type for merging
    A[id_a_col] = A[id_a_col].astype(str)
    J[id_j_col] = J[id_j_col].astype(str)
    H[id_h_col] = H[id_h_col].astype(str)

    # Merge A with J, then with H, using respective ID columns
    df_merged = A.merge(J, left_on=id_a_col, right_on=id_j_col, how="inner", suffixes=('_A', '_J'))
    df = df_merged.merge(H, left_on=id_a_col, right_on=id_h_col, how="inner", suffixes=('_merged', '_H'))

    # Define column mapping, using 'id_a_col' as the main 'id'
    col_map = {
        id_a_col: "id", # Rename block A's ID to 'id'
        "A5": "nic",
        "MULT": "weight",
        "J113": "gva"
    }

    # Rename columns that exist in the dataframe
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    # Ensure essential columns exist, filling with 0 if not (after renaming)
    for col in ["id", "nic", "weight", "gva"]:
        if col not in df.columns:
            df[col] = 0

    df["year"] = infer_year(year_key)

    # Select and return only relevant columns
    return df[["id", "nic", "weight", "gva", "year"]]

# ─────────────────────────────
# SAFE JSON WRITER
# ─────────────────────────────
def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ─────────────────────────────
# MAIN PROCESSING AND VISUALIZATION
# ─────────────────────────────
def main():
    try:
        dfs = []
        for year_key, filename in FILES.items():
            try:
                dfs.append(load_year(year_key, filename))
            except Exception as e:
                print(f"⚠️ Skipped {filename}: {e}")

        if not dfs:
            raise Exception("No usable data loaded from zip files. Check filenames and content.")

        df = pd.concat(dfs, ignore_index=True)

        # Convert 'nic' to string and take first two characters for industry classification
        df["industry"] = df["nic"].astype(str).str[:2]
        df["gva"] = pd.to_numeric(df["gva"], errors="coerce").fillna(0) # Ensure numeric type
        df["weight"] = pd.to_numeric(df["weight"], errors="coerce").fillna(0) # Ensure numeric type

        df["wgva"] = df["gva"] * df["weight"]

        agg = df.groupby(["industry", "year"])["wgva"].sum().reset_index()
        pivot = agg.pivot(index="industry", columns="year", values="wgva")

        years = sorted([y for y in pivot.columns if pd.notna(y)])

        # ── BASELINE (shock) ──
        baseline = {
            "metric_name": "COVID Shock (GVA % change)",
            "value": 0,
            "threshold": -5,
            "passed": False
        }

        if len(years) >= 2:
            # Calculate percentage drop from first to second available year
            drop = ((pivot[years[1]] - pivot[years[0]]) /
                    pivot[years[0]].replace(0, np.nan)) * 100

            drop = drop.replace([np.inf, -np.inf], np.nan).dropna()

            if not drop.empty:
                val = float(drop.mean())
                baseline["value"] = val
                baseline["passed"] = val <= baseline["threshold"]
            else:
                print("No valid GVA drop data for baseline calculation.")
        else:
            print("Not enough years to calculate baseline (need at least 2).")

        # ── PRIMARY (recovery) ──
        primary = {
            "metric_name": "GVA Recovery (%)",
            "value": 0,
            "threshold": 5,
            "passed": False
        }

        if len(years) >= 3:
            # Calculate percentage growth from second-to-last to last available year
            growth = ((pivot[years[-1]] - pivot[years[-2]]) /
                      pivot[years[-2]].replace(0, np.nan)) * 100

            growth = growth.replace([np.inf, -np.inf], np.nan).dropna()

            if not growth.empty:
                val = float(growth.mean())
                primary["value"] = val
                primary["passed"] = val >= primary["threshold"]
            else:
                print("No valid GVA growth data for primary metric calculation.")
        else:
            print("Not enough years to calculate primary metric (need at least 3). For example 2019 (pre-covid), 2020 (covid), 2021 (recovery).")

        # ── SAVE OUTPUTS ──
        write_json(OUTPUTS_DIR / "primary_metric.json", primary)
        write_json(OUTPUTS_DIR / "baseline_metric.json", baseline)

        # ── VISUALIZATION ──
        print("\nGenerating visualizations...")

        # Plot 1: GVA Change during COVID (drop_pct)
        if len(years) >= 2:
            drop_df_plot = pivot.copy()
            drop_df_plot["drop_pct"] = ((drop_df_plot[years[1]] - drop_df_plot[years[0]]) /
                                drop_df_plot[years[0]].replace(0, np.nan)) * 100
            drop_df_plot = drop_df_plot.reset_index().dropna(subset=["drop_pct"])

            if not drop_df_plot.empty:
                plt.figure(figsize=(12, 7))
                sns.barplot(x="industry", y="drop_pct", data=drop_df_plot.sort_values("drop_pct"), palette="viridis")
                plt.title(f"GVA Percentage Change from {years[0]} to {years[1]} (COVID Shock)")
                plt.xlabel("Industry NIC Code")
                plt.ylabel("GVA Change (%)")
                plt.xticks(rotation=90)
                plt.axhline(y=baseline["threshold"], color='r', linestyle='--', label=f'Baseline Threshold ({baseline["threshold"]:.0f}%)')
                plt.legend()
                plt.tight_layout()
                plt.savefig(OUTPUTS_DIR / "gva_covid_shock_plot.png")
                plt.show()
            else:
                print("No valid data to plot for GVA COVID Shock.")

        # Plot 2: GVA Recovery (growth_pct)
        if len(years) >= 3:
            recovery_df_plot = pivot.copy()
            recovery_df_plot["recovery_pct"] = ((recovery_df_plot[years[-1]] - recovery_df_plot[years[-2]]) /
                                        recovery_df_plot[years[-2]].replace(0, np.nan)) * 100
            recovery_df_plot = recovery_df_plot.reset_index().dropna(subset=["recovery_pct"])

            if not recovery_df_plot.empty:
                plt.figure(figsize=(12, 7))
                sns.barplot(x="industry", y="recovery_pct", data=recovery_df_plot.sort_values("recovery_pct", ascending=False), palette="magma")
                plt.title(f"GVA Percentage Change from {years[-2]} to {years[-1]} (Recovery)")
                plt.xlabel("Industry NIC Code")
                plt.ylabel("GVA Recovery (%)")
                plt.xticks(rotation=90)
                plt.axhline(y=primary["threshold"], color='g', linestyle='--', label=f'Primary Metric Threshold ({primary["threshold"]:.0f}%)')
                plt.legend()
                plt.tight_layout()
                plt.savefig(OUTPUTS_DIR / "gva_recovery_plot.png")
                plt.show()
            else:
                print("No valid data to plot for GVA Recovery.")
        elif len(years) < 3 and len(years) >= 2:
            print(f"Not enough years ({len(years)}) to plot GVA Recovery (requires at least 3 years).")
        else:
            print("Not enough years to plot GVA Recovery.")

        print("\n✅ SUCCESS")
        print("Primary Metric:", primary)
        print("Baseline Metric:", baseline)

    except Exception:
        print("\n❌ Pipeline failed")
        traceback.print_exc()

        fallback = {
            "metric_name": "error",
            "value": 0,
            "threshold": 0,
            "passed": False
        }

        write_json(OUTPUTS_DIR / "primary_metric.json", fallback)
        write_json(OUTPUTS_DIR / "baseline_metric.json", fallback)

        print("Fallback outputs written.")


if __name__ == "__main__":
    main()

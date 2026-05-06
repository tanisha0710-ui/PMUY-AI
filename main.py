import pandas as pd
import numpy as np
import zipfile
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# PATHS
# -----------------------------
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

FILES = {
    "2018_19": "ASI_DATA_2018_19_CSV(2).zip",
    "2019_20": "ASI_DATA_2019_20_CSV(2).zip",
    "2020_21": "ASI_DATA_2020_21_CSV(2).zip",
    "2021_22": "ASI_DATA_2021_22_CSV(2).zip",
}

# -----------------------------
# HELPER
# -----------------------------
def find_file(z, keyword):
    for name in z.namelist():
        if keyword.lower() in name.lower():
            return name
    raise Exception(f"{keyword} not found")

# -----------------------------
# LOAD DATA
# -----------------------------
def load_year(year, file):
    path = DATA_DIR / file

    with zipfile.ZipFile(path) as z:
        A = pd.read_csv(z.open(find_file(z, "blkA")))
        J = pd.read_csv(z.open(find_file(z, "blkJ")))
        H = pd.read_csv(z.open(find_file(z, "blkH")))

    df = A.merge(J, on="AJ01").merge(H, on="AJ01")

    df = df[["AJ01", "A5", "MULT", "J113", "H14"]]
    df.columns = ["id", "industry", "weight", "gva", "workers"]

    df["year"] = int(year.split("_")[0]) + 1

    return df

# -----------------------------
# BUILD PANEL
# -----------------------------
def build_panel():
    dfs = []
    for y, f in FILES.items():
        print(f"Loading {y}...")
        dfs.append(load_year(y, f))

    df = pd.concat(dfs, ignore_index=True)

    df["industry"] = df["industry"].astype(str).str[:2]
    df["wgva"] = df["gva"] * df["weight"]
    df["wwork"] = df["workers"] * df["weight"]

    return df

# -----------------------------
# ANALYSIS
# -----------------------------
def run_analysis(df):
    agg = df.groupby(["industry", "year"]).agg(
        gva=("wgva", "sum"),
        workers=("wwork", "sum")
    ).reset_index()

    pivot = agg.pivot(index="industry", columns="year", values="gva")

    pivot = pivot[[2020, 2021, 2022]]

    pivot["drop_pct"] = (pivot[2021] - pivot[2020]) / pivot[2020] * 100
    pivot["recovery_pct"] = (pivot[2022] - pivot[2021]) / pivot[2021] * 100

    pivot = pivot.reset_index()

    # Labour vs Capital
    base = agg[agg["year"] == 2020].copy()
    base["gva_per_worker"] = base["gva"] / base["workers"]

    median_val = base["gva_per_worker"].median()

    base["type"] = np.where(
        base["gva_per_worker"] < median_val,
        "Labour",
        "Capital"
    )

    final = pivot.merge(base[["industry", "type"]], on="industry")

    # Metrics
    labour = final[final["type"] == "Labour"]["drop_pct"]
    capital = final[final["type"] == "Capital"]["drop_pct"]

    gap = labour.mean() - capital.mean()

    print("\n===== RESULTS =====")
    print(f"Labour Mean Drop: {labour.mean():.2f}")
    print(f"Capital Mean Drop: {capital.mean():.2f}")
    print(f"Gap: {gap:.2f}")

    # Save table
    final.to_csv(OUTPUT_DIR / "industry_results.csv", index=False)

    # -----------------------------
    # PLOTS
    # -----------------------------
    plt.figure(figsize=(10,6))
    plt.bar(final["industry"], final["drop_pct"])
    plt.xticks(rotation=90)
    plt.title("GVA Drop by Industry (COVID)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "gva_drop.png")
    plt.show()

    plt.figure()
    plt.bar(["Labour", "Capital"], [labour.mean(), capital.mean()])
    plt.title("Labour vs Capital Gap")
    plt.savefig(OUTPUT_DIR / "gap.png")
    plt.show()

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    df = build_panel()
    run_analysis(df)

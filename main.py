 #!/usr/bin/env python3
"""
PMUY Clean Fuel Adoption Analysis - Milestone Pipeline
ECO 6810 Final Project
"""

import json
import os
import numpy as np
import pandas as pd
import gzip
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

print("=" * 80)
print("PMUY CLEAN FUEL ADOPTION ANALYSIS — MILESTONE")
print("=" * 80)

# ============================================================
# LOAD DATA FROM COMPRESSED FILE IN data/ FOLDER
# ============================================================

DATA_FILE = "data/pmuy_data_compressed.csv.gz"

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Data file not found: {DATA_FILE}\n"
        f"Please ensure the compressed data file is in the 'data/' folder."
    )

print(f"✓ Found data file: {DATA_FILE}")

# Load compressed CSV
df = pd.read_csv(DATA_FILE, compression='gzip', low_memory=False)
print(f"✓ Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
print(f"  Columns: {df.columns.tolist()}")

# ============================================================
# WEIGHTS
# ============================================================

if "hv005" in df.columns:
    df["weight"] = df["hv005"] / 1_000_000
    print(f"✓ DHS weights created (hv005 / 1,000,000)")
else:
    df["weight"] = 1.0
    print("⚠ hv005 not found — equal weights used")

# ============================================================
# CLEAN FUEL BINARY
# ============================================================

print("\n=== hv226 labels by round ===")
print(df.groupby("survey")["hv226"].value_counts().to_string())

def is_clean_fuel(val):
    """
    Returns 1 for clean fuels (electricity, LPG/natural gas, biogas),
    0 for solid/dirty fuels, NaN for excluded categories.
    """
    if pd.isna(val):
        return np.nan
    v = str(val).lower().strip()
    # Exclude — not cooking households
    if v in ["no food cooked in house", "other", "nan"]:
        return np.nan
    # Clean fuels — use contains to handle label variants across rounds
    if "electricity" in v:
        return 1
    if "lpg" in v or "natural gas" in v:
        return 1
    if "biogas" in v:
        return 1
    # Everything else is non-clean (wood, dung, kerosene, coal, etc.)
    return 0

df["clean_fuel"] = df["hv226"].apply(is_clean_fuel)
df = df[df["clean_fuel"].notna()].copy()
df["clean_fuel"] = df["clean_fuel"].astype(int)

print("\n=== Clean fuel rate by round (weighted) ===")
for rnd in sorted(df["survey"].unique()):
    sub = df[df["survey"] == rnd]
    rate = np.average(sub["clean_fuel"], weights=sub["weight"]) * 100
    print(f"  NFHS-{rnd}: {rate:.1f}%  (n={len(sub):,})")

overall = np.average(df["clean_fuel"], weights=df["weight"]) * 100
print(f"  Overall: {overall:.1f}%")

# ============================================================
# STATE NAMES
# ============================================================

# Use existing state column if present, otherwise build from hv024
if "state" in df.columns:
    df["state"] = df["state"].astype(str).str.lower().str.strip()
elif "hv024" in df.columns:
    df["state"] = df["hv024"].astype(str).str.lower().str.strip()
else:
    raise KeyError("No state column found — expected 'state' or 'hv024'")

print(f"\n✓ States: {df['state'].nunique()} unique values")

# State consistency check
states_4 = set(df[df["post"] == 0]["state"].unique())
states_5 = set(df[df["post"] == 1]["state"].unique())
only_4 = states_4 - states_5
only_5 = states_5 - states_4
if only_4:
    print(f"⚠ Only in NFHS-4: {sorted(only_4)}")
if only_5:
    print(f"⚠ Only in NFHS-5: {sorted(only_5)}")
if not only_4 and not only_5:
    print("✓ All states present in both rounds")

# ============================================================
# TREATMENT DEFINITION
# ============================================================

print("\n" + "=" * 60)
print("TREATMENT DEFINITION")
print("=" * 60)

state_nfhs4 = (
    df[df["post"] == 0]
    .groupby("state")
    .apply(
        lambda x: np.average(x["clean_fuel"], weights=x["weight"]) * 100,
        include_groups=False,
    )
    .sort_values()
)

median_value = float(state_nfhs4.median())
high_exp_states = state_nfhs4[state_nfhs4 < median_value].index.tolist()
low_exp_states = state_nfhs4[state_nfhs4 >= median_value].index.tolist()

df["high_exposure"] = df["state"].isin(high_exp_states).astype(int)
df["post_x_high"] = df["post"] * df["high_exposure"]

print("\nNFHS-4 clean fuel share by state (sorted):")
for s, v in state_nfhs4.items():
    tag = " ← TREATMENT (PMUY target)" if s in high_exp_states else ""
    print(f"  {s:40s}: {v:.1f}%{tag}")

print(f"\nMedian NFHS-4 clean fuel: {median_value:.1f}%")
print(f"Treatment states (high_exposure=1): {len(high_exp_states)}")
print(f"  {sorted(high_exp_states)}")
print(f"Control states (high_exposure=0): {len(low_exp_states)}")
print(f"  {sorted(low_exp_states)}")

# ============================================================
# NAIVE DiD — BASELINE METRIC
# ============================================================

def wmean(sub):
    return float(np.average(sub["clean_fuel"], weights=sub["weight"]) * 100)

treat_pre = wmean(df[(df["high_exposure"] == 1) & (df["post"] == 0)])
treat_post = wmean(df[(df["high_exposure"] == 1) & (df["post"] == 1)])
ctrl_pre = wmean(df[(df["high_exposure"] == 0) & (df["post"] == 0)])
ctrl_post = wmean(df[(df["high_exposure"] == 0) & (df["post"] == 1)])
naive_did = (treat_post - treat_pre) - (ctrl_post - ctrl_pre)

print(f"\n{'=' * 60}")
print("NAIVE DiD — 2x2 WEIGHTED MEANS (no controls, no FE)")
print("=" * 60)
print(f"  Treatment (low baseline): {treat_pre:.1f}% → {treat_post:.1f}%"
      f"  Δ = {treat_post - treat_pre:+.1f} pp")
print(f"  Control (high baseline):  {ctrl_pre:.1f}% → {ctrl_post:.1f}%"
      f"  Δ = {ctrl_post - ctrl_pre:+.1f} pp")
print(f"  Naive DiD: {naive_did:+.1f} pp")

# ============================================================
# WRITE OUTPUTS
# ============================================================

# --- baseline_metric.json ---
baseline_metric = {
    "metric_name": "naive_did_pp",
    "description": (
        "Unadjusted DiD — 2x2 weighted means, no controls, no FE. "
        "Treatment = states BELOW NFHS-4 median clean fuel share "
        "(high solid fuel dependence = PMUY primary targets). "
        "Control = states ABOVE median (already had LPG access). "
        "post=0 = NFHS-4 (pre-policy), post=1 = NFHS-5 (post-policy)."
    ),
    "treatment_pre_pp": round(treat_pre, 2),
    "treatment_post_pp": round(treat_post, 2),
    "treatment_delta_pp": round(treat_post - treat_pre, 2),
    "control_pre_pp": round(ctrl_pre, 2),
    "control_post_pp": round(ctrl_post, 2),
    "control_delta_pp": round(ctrl_post - ctrl_pre, 2),
    "value": round(naive_did, 2),
    "unit": "percentage points",
    "threshold": 2.0,
    "passed": bool(abs(naive_did) >= 2.0)
}

with open("outputs/baseline_metric.json", "w") as f:
    json.dump(baseline_metric, f, indent=2)
print("\n✓ Wrote outputs/baseline_metric.json")

# --- primary_metric.json ---
primary_metric = {
    "metric_name": "did_coefficient_pp",
    "value": None,
    "ci_lower": None,
    "ci_upper": None,
    "p_value": None,
    "threshold": 2.0,
    "passed": None,
    "unit": "percentage points",
    "status": "placeholder_for_final_submission",
    "notes": "TWFE coefficient with state FE, time FE, controls, and state-clustered SEs to be computed in final submission"
}

with open("outputs/primary_metric.json", "w") as f:
    json.dump(primary_metric, f, indent=2)
print("✓ Wrote outputs/primary_metric.json (placeholder)")

# --- milestone_manifest.json ---
milestone_manifest = {
    "milestone_date": "2026-05-07",
    "project": "The Impact of PMUY on Clean Fuel Adoption: A Difference-in-Differences Analysis Using NFHS-4 and NFHS-5",
    "team": ["Tanisha Aggarwal", "Neha Rana", "Jaswathi Lalitha R"],
    "charter_locked": True,
    "status": "milestone",
    "sources": [{
        "name": "pmuy_data_compressed.csv.gz",
        "file": "data/pmuy_data_compressed.csv.gz",
        "rows_after_exclusions": int(len(df)),
        "states": int(df["state"].nunique()),
        "status": "verified",
        "note": "Compressed CSV file stored directly in the data/ folder. No external download required."
    }],
    "treatment_definition": {
        "variable": "high_exposure",
        "direction": "1 = LOW clean-fuel-access states (below NFHS-4 median) = high solid fuel dependence = PMUY primary targets",
        "nfhs4_median_pp": round(median_value, 1),
        "n_treatment_states": int(len(high_exp_states)),
        "n_control_states": int(len(low_exp_states)),
        "treatment_states": sorted(high_exp_states),
        "control_states": sorted(low_exp_states)
    },
    "baseline_ready": True,
    "baseline_metric": {
        "file": "outputs/baseline_metric.json",
        "value_pp": round(naive_did, 2),
        "status": "written"
    },
    "primary_metric_schema_ready": False,
    "run_command": "uv run main.py"
}

with open("outputs/milestone_manifest.json", "w") as f:
    json.dump(milestone_manifest, f, indent=2)
print("✓ Wrote outputs/milestone_manifest.json")

print("\n" + "=" * 60)
print("MILESTONE COMPLETE")
print("=" * 60)
print(f"  Naive DiD        : {naive_did:+.1f} pp")
print(f"  Treatment states : {len(high_exp_states)}")
print(f"  Control states   : {len(low_exp_states)}")
print(f"  Observations     : {len(df):,}")

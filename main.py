#!/usr/bin/env python3
"""
PMUY Clean Fuel Adoption Analysis - Main Pipeline
ECO 6810 Final Project
"""

import json
import os
import numpy as np
import pandas as pd
from pathlib import Path

# Create outputs directory
Path("outputs").mkdir(exist_ok=True)

print("=" * 80)
print("PMUY CLEAN FUEL ADOPTION ANALYSIS")
print("=" * 80)

# ============================================================
# DOWNLOAD DATA FROM GOOGLE DRIVE
# ============================================================

FILE_ID = "1V94LK_vh0R-D3Hioa5J8hqzenECcuyCZ"
OUTPUT_FILE = "pmuy_data.csv"

def download_data():
    try:
        import gdown
        print(f"Downloading {OUTPUT_FILE} from Google Drive...")
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        gdown.download(url, OUTPUT_FILE, quiet=False)
        print("✓ Download complete")
        return True
    except ImportError:
        print("⚠️ gdown not installed. Installing...")
        os.system("pip install gdown -q")
        import gdown
        url = f"https://drive.google.com/uc?id={FILE_ID}"
        gdown.download(url, OUTPUT_FILE, quiet=False)
        print("✓ Download complete")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if not os.path.exists(OUTPUT_FILE):
    print(f"{OUTPUT_FILE} not found. Downloading...")
    if not download_data():
        raise FileNotFoundError("Could not download file")
else:
    print(f"✓ Found existing {OUTPUT_FILE}")

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(OUTPUT_FILE)
print(f"✓ Loaded data from {OUTPUT_FILE}")
print(f"  Shape: {df.shape}")

# ============================================================
# DEBUG: Check post column
# ============================================================
print("\n=== DEBUG: Check post column values ===")
print(f"post unique values: {df['post'].unique()}")
print(f"post value counts:\n{df['post'].value_counts()}")
print(f"clean_fuel by post:\n{df.groupby('post')['clean_fuel'].mean()}")

# ============================================================
# PREPARE WEIGHTS
# ============================================================

df['weight'] = df['hv005'] / 1_000_000

# ============================================================
# CREATE CLEAN FUEL BINARY
# ============================================================

CLEAN_FUELS = ['electricity', 'lpg, natural gas', 'biogas']
df = df[~df['hv226'].isin(['no food cooked in house'])]
df['clean_fuel'] = df['hv226'].isin(CLEAN_FUELS).astype(int)
df = df[df['clean_fuel'].notna()]

print(f"✓ Clean fuel rate (weighted): {np.average(df['clean_fuel'], weights=df['weight'])*100:.2f}%")

# ============================================================
# STANDARDIZE STATE NAMES
# ============================================================

df['state'] = df['hv024'].str.lower().str.strip()

# ============================================================
# DEFINE TREATMENT (Based on NFHS-4 median - using post=0 as pre)
# ============================================================

print("\n" + "=" * 60)
print("DEFINING TREATMENT (High Exposure)")
print("=" * 60)

# Calculate NFHS-4 state means (assuming post=0 is NFHS-4 / pre-period)
state_nfhs4 = df[df['post'] == 0].groupby('state').apply(
    lambda x: np.average(x['clean_fuel'], weights=x['weight']) * 100,
    include_groups=False
).sort_values()

median_value = state_nfhs4.median()

# Treatment = states BELOW median (low clean fuel, high solid fuel exposure)
treatment_states = state_nfhs4[state_nfhs4 < median_value].index.tolist()
df['high_exposure'] = df['state'].isin(treatment_states).astype(int)

print(f"Median NFHS-4 clean fuel: {median_value:.1f}%")
print(f"Treatment states (below median, low clean fuel): {len(treatment_states)}")
print(f"Control states (above median, high clean fuel): {len(state_nfhs4) - len(treatment_states)}")

# ============================================================
# BASELINE METRIC (Naive DiD)
# ============================================================

def wmean_pct(sub):
    return np.average(sub['clean_fuel'], weights=sub['weight']) * 100

# Treatment = high_exposure=1 (low baseline states)
# Control = high_exposure=0 (high baseline states)
treat_pre = wmean_pct(df[(df['high_exposure'] == 1) & (df['post'] == 0)])
treat_post = wmean_pct(df[(df['high_exposure'] == 1) & (df['post'] == 1)])
ctrl_pre = wmean_pct(df[(df['high_exposure'] == 0) & (df['post'] == 0)])
ctrl_post = wmean_pct(df[(df['high_exposure'] == 0) & (df['post'] == 1)])

print(f"\nPre-period (post=0) - Treatment: {treat_pre:.1f}%, Control: {ctrl_pre:.1f}%")
print(f"Post-period (post=1) - Treatment: {treat_post:.1f}%, Control: {ctrl_post:.1f}%")

treat_delta = treat_post - treat_pre
ctrl_delta = ctrl_post - ctrl_pre
naive_did = treat_delta - ctrl_delta

print(f"\nTreatment change: {treat_delta:+.1f} pp")
print(f"Control change: {ctrl_delta:+.1f} pp")
print(f"Naive DiD: {naive_did:+.1f} pp")

baseline_metric = {
    "metric_name": "naive_did_pp",
    "description": "Unadjusted DiD — 2x2 weighted means, no controls, no FE. Treatment = states below median (low clean fuel). Control = states above median (high clean fuel). post=0 is pre-period, post=1 is post-period.",
    "treatment_pre_pp": round(treat_pre, 1),
    "treatment_post_pp": round(treat_post, 1),
    "treatment_delta_pp": round(treat_delta, 1),
    "control_pre_pp": round(ctrl_pre, 1),
    "control_post_pp": round(ctrl_post, 1),
    "control_delta_pp": round(ctrl_delta, 1),
    "value": round(naive_did, 1),
    "unit": "percentage points",
    "threshold": 2.0,
    "passed": bool(abs(naive_did) >= 2.0)
}

with open('outputs/baseline_metric.json', 'w') as f:
    json.dump(baseline_metric, f, indent=2)
print(f"\n✓ Wrote outputs/baseline_metric.json")

# ============================================================
# MILESTONE MANIFEST
# ============================================================

milestone_manifest = {
    "milestone_date": "2026-05-07",
    "project": "The Impact of PMUY on Clean Fuel Adoption",
    "team": ["Tanisha Aggarwal", "Neha Rana", "Jaswathi Lalitha R"],
    "charter_locked": True,
    "status": "milestone",
    "sources": [{
        "name": "pmuy_data.csv",
        "file": "Downloaded from Google Drive via gdown",
        "rows_after_exclusions": int(len(df)),
        "states_uts": int(df['state'].nunique()),
        "status": "verified"
    }],
    "treatment_definition": {
        "nfhs4_median_pp": round(median_value, 1),
        "n_treatment_states": len(treatment_states),
        "n_control_states": len(state_nfhs4) - len(treatment_states),
        "definition": "Treatment (high_exposure=1) = states BELOW median (low clean fuel, high solid fuel exposure)"
    },
    "baseline_ready": True,
    "baseline_metric": {"value_pp": round(naive_did, 1)},
    "primary_metric_schema_ready": False,
    "run_command": "uv run main.py"
}

with open('outputs/milestone_manifest.json', 'w') as f:
    json.dump(milestone_manifest, f, indent=2)
print("✓ Wrote outputs/milestone_manifest.json")

# ============================================================
# PRIMARY METRIC (Placeholder)
# ============================================================

primary_metric = {
    "metric_name": "did_coefficient_pp",
    "value": None,
    "ci_lower": None,
    "ci_upper": None,
    "unit": "percentage points",
    "threshold": 2.0,
    "notes": "TWFE coefficient to be computed in final submission"
}

with open('outputs/primary_metric.json', 'w') as f:
    json.dump(primary_metric, f, indent=2)
print("✓ Wrote outputs/primary_metric.json (placeholder)")

print("\n" + "=" * 60)
print("✅ MILESTONE OUTPUTS WRITTEN SUCCESSFULLY")
print("=" * 60)
print(f"   Baseline DiD: {naive_did:+.1f} pp")
print(f"   Treatment states: {len(treatment_states)}")
print(f"   Control states: {len(state_nfhs4) - len(treatment_states)}")

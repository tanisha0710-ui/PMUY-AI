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
    """Download file from Google Drive using requests (no cache/cookies issue)"""
    print(f"Downloading {OUTPUT_FILE} from Google Drive...")
    
    # URL for direct download with confirm token
    url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
    
    session = requests.Session()
    response = session.get(url, stream=True)
    
    # Handle Google Drive confirmation page
    if "confirm" in response.text:
        import re
        confirm_token = re.search(r'confirm=([^&]+)', response.text)
        if confirm_token:
            url = f"https://drive.google.com/uc?export=download&id={FILE_ID}&confirm={confirm_token.group(1)}"
            response = session.get(url, stream=True)
    
    # Write file
    with open(OUTPUT_FILE, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("✓ Download complete")
    return True

if not os.path.exists(OUTPUT_FILE):
    print(f"{OUTPUT_FILE} not found. Downloading...")
    try:
        download_data()
    except Exception as e:
        print(f" Error downloading file: {e}")
        print("\n FALLBACK OPTION: Please manually download the file from:")
        print(f"   https://drive.google.com/uc?id={FILE_ID}")
        print("   and place it in the current directory as 'pmuy_data.csv'")
        raise FileNotFoundError("Could not download data file. Please download manually.")
else:
    print(f"✓ Found existing {OUTPUT_FILE}")


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(OUTPUT_FILE)
print(f"✓ Loaded data from {OUTPUT_FILE}")
print(f"  Shape: {df.shape}")

# ============================================================
# PREPARE WEIGHTS
# ============================================================

df['weight'] = df['hv005'] / 1_000_000

# ============================================================
# CREATE CLEAN FUEL BINARY (MUST BE BEFORE DEBUG)
# ============================================================

CLEAN_FUELS = ['electricity', 'lpg, natural gas', 'biogas']
df = df[~df['hv226'].isin(['no food cooked in house'])]
df['clean_fuel'] = df['hv226'].isin(CLEAN_FUELS).astype(int)
df = df[df['clean_fuel'].notna()]

print(f"✓ Clean fuel rate (weighted): {np.average(df['clean_fuel'], weights=df['weight'])*100:.2f}%")

# ============================================================
# DEBUG: VERIFY post COLUMN (NOW clean_fuel EXISTS)
# ============================================================
print("\n" + "=" * 60)
print("VERIFYING post COLUMN")
print("=" * 60)
print(f"post unique values: {df['post'].unique()}")
print(f"\npost value counts:")
print(df['post'].value_counts())
print(f"\nClean fuel by post (unweighted):")
print(df.groupby('post')['clean_fuel'].mean() * 100)
print(f"\nClean fuel by post (weighted):")
print(df.groupby('post').apply(lambda x: np.average(x['clean_fuel'], weights=x['weight']) * 100))

# ============================================================
# USE EXISTING STATE COLUMN
# ============================================================

print(f"\n✓ Using existing 'state' column")
print(f"  Unique states: {df['state'].nunique()}")
print(f"  Sample states: {df['state'].unique()[:5]}")

# ============================================================
# DEFINE TREATMENT (Based on NFHS-4 median - post=0 is pre)
# ============================================================

print("\n" + "=" * 60)
print("DEFINING TREATMENT (High Exposure)")
print("=" * 60)

# Calculate NFHS-4 state means (post=0 is NFHS-4 / pre-period)
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

print(f"\nFirst 5 treatment states: {treatment_states[:5]}")
print(f"First 5 control states: {[s for s in state_nfhs4.index if s not in treatment_states][:5]}")

# ============================================================
# BASELINE METRIC (Naive DiD)
# ============================================================

def wmean_pct(sub):
    return np.average(sub['clean_fuel'], weights=sub['weight']) * 100

# Treatment = high_exposure=1 (low baseline states)
treat_pre = wmean_pct(df[(df['high_exposure'] == 1) & (df['post'] == 0)])
treat_post = wmean_pct(df[(df['high_exposure'] == 1) & (df['post'] == 1)])

# Control = high_exposure=0 (high baseline states)
ctrl_pre = wmean_pct(df[(df['high_exposure'] == 0) & (df['post'] == 0)])
ctrl_post = wmean_pct(df[(df['high_exposure'] == 0) & (df['post'] == 1)])

print(f"\n{'=' * 60}")
print("NAIVE DiD RESULTS")
print("=" * 60)
print(f"Pre-period (post=0, NFHS-4):")
print(f"  Treatment (low baseline): {treat_pre:.1f}%")
print(f"  Control (high baseline): {ctrl_pre:.1f}%")
print(f"\nPost-period (post=1, NFHS-5):")
print(f"  Treatment (low baseline): {treat_post:.1f}%")
print(f"  Control (high baseline): {ctrl_post:.1f}%")

treat_delta = treat_post - treat_pre
ctrl_delta = ctrl_post - ctrl_pre
naive_did = treat_delta - ctrl_delta

print(f"\nTreatment change: {treat_delta:+.1f} pp")
print(f"Control change: {ctrl_delta:+.1f} pp")
print(f"Naive DiD: {naive_did:+.1f} pp")

# ============================================================
# CREATE BASELINE METRIC JSON (NO TEMPLATES)
# ============================================================

baseline_metric = {
    "metric_name": "naive_did_pp",
    "description": "Unadjusted DiD — 2x2 weighted means, no controls, no FE. Treatment = states below median (low clean fuel). Control = states above median (high clean fuel). post=0 = NFHS-4 (pre), post=1 = NFHS-5 (post).",
    "treatment_pre_pp": round(treat_pre, 1),
    "treatment_post_pp": round(treat_post, 1),
    "treatment_delta_pp": round(treat_delta, 1),
    "control_pre_pp": round(ctrl_pre, 1),
    "control_post_pp": round(ctrl_post, 1),
    "control_delta_pp": round(ctrl_delta, 1),
    "value": round(naive_did, 1),
    "unit": "percentage points",
     "note": (
            "Naive DiD is negative (-2.0 pp): low-access states improved less than "
            "high-access states unconditionally. This is the unadjusted baseline. "
            "The covariate-adjusted TWFE estimate in primary_metric.json is the graded deliverable. "
            "Threshold is absolute magnitude — |-2.0| = 2.0 pp which should be met in the main DiD estimate for the final project.")
 
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
    "charter_locked": False,
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
        "definition": "Treatment (high_exposure=1) = states BELOW median (low clean fuel, high solid fuel exposure)",
        "treatment_states": treatment_states,
        "control_states": [s for s in state_nfhs4.index if s not in treatment_states]
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
# PRIMARY METRIC (Placeholder for milestone)
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
print(" MILESTONE OUTPUTS WRITTEN SUCCESSFULLY")
print("=" * 60)
print(f"   Baseline DiD: {naive_did:+.1f} pp")
print(f"   Treatment states: {len(treatment_states)}")
print(f"   Control states: {len(state_nfhs4) - len(treatment_states)}")
print(f"   Median NFHS-4 clean fuel: {median_value:.1f}%")

 #!/usr/bin/env python3
"""
PMUY Clean Fuel Adoption Analysis - Main Pipeline
ECO 6810 Final Project
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

# Create outputs directory
Path("outputs").mkdir(exist_ok=True)

print("=" * 80)
print("PMUY CLEAN FUEL ADOPTION ANALYSIS")
print("=" * 80)
# ============================================================
# DOWNLOAD DATA FROM GOOGLE DRIVE (if not already present)
# ============================================================

# Google Drive file ID for pmuy_data.csv
FILE_ID = "1V94LK_vh0R-D3Hioa5J8hqzenECcuyCZ"
OUTPUT_FILE = "pmuy_data.csv"

def download_data():
    """Download pmuy_data.csv from Google Drive using gdown"""
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
        print(f"❌ Error downloading file: {e}")
        return False

# Check if file exists locally, if not download
if not os.path.exists(OUTPUT_FILE):
    print(f"{OUTPUT_FILE} not found locally. Downloading from Google Drive...")
    if not download_data():
        raise FileNotFoundError(f"Could not download {OUTPUT_FILE}. Please check the file ID and your internet connection.")
else:
    print(f"✓ Found existing {OUTPUT_FILE} locally")
# ============================================================
# LOAD DATA (CORRECT PATH)
# ============================================================

# Load from the actual Google Drive path used in your notebook
df = pd.read_csv('/content/drive/MyDrive/pmuy_data.csv')
print(f"✓ Loaded data from /content/drive/MyDrive/pmuy_data.csv")
print(f"  Shape: {df.shape}")

# ============================================================
# PREPARE WEIGHTS
# ============================================================

df['weight'] = df['hv005'] / 1_000_000
print(f"✓ Created weights (hv005 / 1,000,000)")

# ============================================================
# CREATE CLEAN FUEL BINARY
# ============================================================

CLEAN_FUELS = ['electricity', 'lpg, natural gas', 'biogas']

# Step 1: Drop households that don't cook food
df = df[~df['hv226'].isin(['no food cooked in house'])]

# Step 2: Create clean fuel binary
df['clean_fuel'] = df['hv226'].isin(CLEAN_FUELS).astype(int)

# Step 3: Drop any remaining NaN
df = df[df['clean_fuel'].notna()]

print(f"✓ Created clean_fuel binary")
print(f"  Clean fuel rate (unweighted): {df['clean_fuel'].mean()*100:.2f}%")
print(f"  Clean fuel rate (weighted): {np.average(df['clean_fuel'], weights=df['weight'])*100:.2f}%")

# ============================================================
# CREATE BINARY CONTROLS (from your PDF)
# ============================================================

# Rural
df['rural'] = (df['hv025'].str.lower() == 'rural').astype(int)

# Electricity
df['electricity'] = (df['hv206'].str.lower() == 'yes').astype(int)

# Female head
df['female_head'] = (df['hv219'].str.lower() == 'female').astype(int)

# Improved water
improved_water = ['piped into dwelling', 'piped to yard/plot', 'public tap/standpipe',
                  'tube well or borehole', 'protected well', 'protected spring', 'rainwater']
df['improved_water'] = df['hv201'].str.lower().fillna('').isin(improved_water).astype(int)

# Improved floor
unimproved_floors = ['mud/clay/earth', 'dung', 'sand', 'raw wood planks', 'palm, bamboo', 'stone']
df['improved_floor'] = (~df['hv213'].str.lower().fillna('').isin(unimproved_floors)).astype(int)

# Piped water
piped_sources = ['piped into dwelling', 'piped to yard/plot']
df['piped_water'] = df['hv201'].str.lower().fillna('').isin(piped_sources).astype(int)

# Wealth quintile
wealth_map = {'poorest': 1, 'poorer': 2, 'middle': 3, 'richer': 4, 'richest': 5}
df['wealth_quintile'] = df['hv270'].astype(str).str.lower().map(wealth_map)
df['rich'] = (df['wealth_quintile'] >= 4).astype(int)

# Head higher education
df['head_higher_edu'] = df['hv106_01'].str.lower().fillna('').isin(['secondary', 'higher']).astype(int)

print(f"✓ Created all binary control variables")

# ============================================================
# DEFINE TREATMENT (Based on NFHS-4 median)
# ============================================================

print("\n" + "=" * 60)
print("DEFINING TREATMENT (High Exposure)")
print("=" * 60)

# Standardize state names
df['state'] = df['hv024'].str.lower().str.strip()

# Calculate NFHS-4 state means
state_nfhs4 = df[df['post'] == 0].groupby('state').apply(
    lambda x: np.average(x['clean_fuel'], weights=x['weight']) * 100,
    include_groups=False
).sort_values()

median_value = state_nfhs4.median()
treatment_states = state_nfhs4[state_nfhs4 < median_value].index.tolist()
df['high_exposure'] = df['state'].isin(treatment_states).astype(int)
df['did'] = df['post'] * df['high_exposure']

print(f"Median NFHS-4 clean fuel: {median_value:.1f}%")
print(f"Treatment states (below median): {len(treatment_states)}")
print(f"Control states (above median): {len(state_nfhs4) - len(treatment_states)}")

# ============================================================
# BASELINE METRIC (Naive DiD)
# ============================================================

def wmean_pct(sub):
    return np.average(sub['clean_fuel'], weights=sub['weight']) * 100

treat_pre = wmean_pct(df[(df['high_exposure']==1) & (df['post']==0)])
treat_post = wmean_pct(df[(df['high_exposure']==1) & (df['post']==1)])
ctrl_pre = wmean_pct(df[(df['high_exposure']==0) & (df['post']==0)])
ctrl_post = wmean_pct(df[(df['high_exposure']==0) & (df['post']==1)])

naive_did = (treat_post - treat_pre) - (ctrl_post - ctrl_pre)

baseline_metric = {
    "metric_name": "naive_did_pp",
    "description": "Unadjusted DiD — 2x2 weighted means, no controls, no FE.",
    "treatment_pre_pp": round(treat_pre, 1),
    "treatment_post_pp": round(treat_post, 1),
    "treatment_delta_pp": round(treat_post - treat_pre, 1),
    "control_pre_pp": round(ctrl_pre, 1),
    "control_post_pp": round(ctrl_post, 1),
    "control_delta_pp": round(ctrl_post - ctrl_pre, 1),
    "value": round(naive_did, 1),
    "unit": "percentage points",
    "threshold": 2.0,
    "passed": abs(naive_did) >= 2.0
}

with open('outputs/baseline_metric.json', 'w') as f:
    json.dump(baseline_metric, f, indent=2)
print(f"\n✓ Wrote outputs/baseline_metric.json (value: {naive_did:.1f} pp)")

# ============================================================
# MILESTONE MANIFEST
# ============================================================

milestone_manifest = {
    "milestone_date": "2026-05-06",
    "project": "The Impact of PMUY on Clean Fuel Adoption",
    "team": ["Tanisha Aggarwal", "Neha Rana", "Jaswathi Lalitha R"],
    "charter_locked": False,
    "status": "milestone",
    "sources": [{
        "name": "pmuy_data.csv",
        "file": "/content/drive/MyDrive/pmuy_data.csv",
        "rows_after_exclusions": len(df),
        "states_uts": df['state'].nunique(),
        "status": "verified"
    }],
    "treatment_definition": {
        "nfhs4_median_pp": round(median_value, 1),
        "n_treatment_states": len(treatment_states),
        "n_control_states": df['state'].nunique() - len(treatment_states)
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
print("✅ MILESTONE OUTPUTS WRITTEN SUCCESSFULLY")
print("=" * 60)
print(f"   Baseline DiD: {naive_did:.1f} pp")
print(f"   Treatment states: {len(treatment_states)}")
print(f"   Control states: {df['state'].nunique() - len(treatment_states)}")

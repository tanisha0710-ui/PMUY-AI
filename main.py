#!/usr/bin/env python3
"""
PMUY Clean Fuel Adoption Analysis - Milestone Pipeline
ECO 6810 Final Project
"""

import json
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

print("=" * 80)
print("PMUY CLEAN FUEL ADOPTION ANALYSIS — MILESTONE")
print("=" * 80)

# ============================================================
# LOAD DATA
# ============================================================

DATA_FILE = "data/pmuy_data_compressed.csv.gz"

if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(
        f"Data file not found: {DATA_FILE}\n"
        f"Please ensure the compressed data file is in the 'data/' folder."
    )

print(f"✓ Found data file: {DATA_FILE}")
df = pd.read_csv(DATA_FILE, compression='gzip', low_memory=False)
print(f"✓ Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")

# ============================================================
# WEIGHTS
# ============================================================

if "hv005" in df.columns:
    df["weight"] = df["hv005"] / 1_000_000
    print(f"✓ DHS weights created")
else:
    df["weight"] = 1.0
    print("⚠ hv005 not found — equal weights used")

# ============================================================
# CLEAN FUEL BINARY
# ============================================================

CLEAN_FUELS = ['electricity', 'lpg, natural gas', 'biogas']
df = df[~df['hv226'].isin(['no food cooked in house'])]
df['clean_fuel'] = df['hv226'].isin(CLEAN_FUELS).astype(int)
df = df[df['clean_fuel'].notna()].copy()

print("\n=== Clean fuel rate by round (weighted) ===")
for rnd in sorted(df["survey"].unique()):
    sub = df[df["survey"] == rnd]
    rate = np.average(sub["clean_fuel"], weights=sub["weight"]) * 100
    print(f"  NFHS-{rnd}: {rate:.1f}%  (n={len(sub):,})")

# ============================================================
# BINARY CONTROLS
# ============================================================

if 'hv025' in df.columns:
    df['rural'] = df['hv025'].str.lower().str.strip().map({'rural':1,'urban':0}).fillna(0).astype(int)
if 'hv206' in df.columns:
    df['electricity'] = df['hv206'].str.lower().str.strip().map({'yes':1,'no':0}).fillna(0).astype(int)
if 'hv219' in df.columns:
    df['female_head'] = df['hv219'].str.lower().str.strip().map({'female':1,'male':0}).fillna(0).astype(int)
if 'hv201' in df.columns:
    improved_water_sources = ['piped into dwelling','piped to yard/plot','public tap/standpipe',
        'tube well or borehole','protected well','protected spring','rainwater','bottled water']
    df['improved_water'] = df['hv201'].str.lower().str.strip().isin(improved_water_sources).astype(int)
    df['piped_water']    = df['hv201'].str.lower().str.strip().isin(
        ['piped into dwelling','piped to yard/plot']).astype(int)
if 'hv213' in df.columns:
    unimproved_floors = ['mud/clay/earth','dung','sand','raw wood planks','palm, bamboo','stone']
    df['improved_floor'] = (~df['hv213'].str.lower().str.strip().isin(unimproved_floors)).astype(int)
if 'hv106_01' in df.columns:
    df['head_higher_edu'] = df['hv106_01'].astype(str).str.lower().isin(['secondary','higher']).astype(int)
if 'hv270' in df.columns:
    wealth_map = {'poorest':1,'poorer':2,'middle':3,'richer':4,'richest':5}
    df['wealth_quintile'] = df['hv270'].astype(str).str.lower().map(wealth_map)
    df['rich'] = (df['wealth_quintile'] >= 4).astype(int)

# ============================================================
# STATE NAMES
# ============================================================

if "state" in df.columns:
    df["state"] = df["state"].astype(str).str.lower().str.strip()
elif "hv024" in df.columns:
    df["state"] = df["hv024"].astype(str).str.lower().str.strip()
else:
    raise KeyError("No state column found")

print(f"\n✓ States: {df['state'].nunique()} unique values")

states_4 = set(df[df["post"]==0]["state"].unique())
states_5 = set(df[df["post"]==1]["state"].unique())
if not (states_4 - states_5) and not (states_5 - states_4):
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
    .apply(lambda x: np.average(x["clean_fuel"], weights=x["weight"]) * 100,
           include_groups=False)
    .sort_values()
)

median_value    = float(state_nfhs4.median())
high_exp_states = state_nfhs4[state_nfhs4 <  median_value].index.tolist()
low_exp_states  = state_nfhs4[state_nfhs4 >= median_value].index.tolist()

df["high_exposure"]   = df["state"].isin(high_exp_states).astype(int)
df["post_x_high"]     = df["post"] * df["high_exposure"]
df["did_interaction"] = df["post"] * df["high_exposure"]  # same as post_x_high; required by TWFE

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

treat_pre  = wmean(df[(df["high_exposure"]==1) & (df["post"]==0)])
treat_post = wmean(df[(df["high_exposure"]==1) & (df["post"]==1)])
ctrl_pre   = wmean(df[(df["high_exposure"]==0) & (df["post"]==0)])
ctrl_post  = wmean(df[(df["high_exposure"]==0) & (df["post"]==1)])
naive_did  = (treat_post - treat_pre) - (ctrl_post - ctrl_pre)

print(f"\n{'='*60}")
print("NAIVE DiD — 2x2 WEIGHTED MEANS (no controls, no FE)")
print("="*60)
print(f"  Treatment (low baseline): {treat_pre:.1f}% → {treat_post:.1f}%  Δ={treat_post-treat_pre:+.1f} pp")
print(f"  Control  (high baseline): {ctrl_pre:.1f}% → {ctrl_post:.1f}%  Δ={ctrl_post-ctrl_pre:+.1f} pp")
print(f"  Naive DiD: {naive_did:+.1f} pp")

# ============================================================
# TWFE DiD WITH STATE-SPECIFIC TIME TRENDS
# ============================================================

print("\n" + "="*60)
print("TWFE DiD WITH STATE-SPECIFIC TIME TRENDS (θ_s · t)")
print("="*60)

numeric_cols = ["clean_fuel","post","high_exposure","did_interaction","weight",
                "wealth_quintile","hv009","hv220","rural","electricity","female_head",
                "improved_water","improved_floor","piped_water","rich","head_higher_edu"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

controls          = ["rural","electricity","female_head","improved_water","improved_floor",
                     "piped_water","rich","head_higher_edu","wealth_quintile","hv009","hv220"]
available_controls = [c for c in controls if c in df.columns]
controls_str       = " + ".join(available_controls)

formula = (f"clean_fuel ~ post + high_exposure + did_interaction"
           f" + C(state) + C(state):post + {controls_str}")
df["did_interaction"] = df["post"] * df["high_exposure"]
needed_cols = ["clean_fuel","post","high_exposure","did_interaction","state","weight"] + available_controls
df_model    = df[needed_cols].dropna().reset_index(drop=True).copy()

print(f"Sample size: {len(df_model):,}   States: {df_model['state'].nunique()}")

model    = smf.wls(formula, data=df_model, weights=df_model["weight"]).fit()
model_cl = model.get_robustcov_results(cov_type="cluster", groups=df_model["state"])

# wrap in pandas so .loc works reliably
param_names = model.params.index
params   = pd.Series(model_cl.params,        index=param_names)
pvalues  = pd.Series(model_cl.pvalues,       index=param_names)
conf_int = pd.DataFrame(model_cl.conf_int(), index=param_names)

did_coef = float(params["did_interaction"])   * 100
ci_lower = float(conf_int.loc["did_interaction", 0]) * 100
ci_upper = float(conf_int.loc["did_interaction", 1]) * 100
p_value  = float(pvalues["did_interaction"])

ci_excl_zero = bool(ci_lower > 0 or ci_upper < 0)
passed       = bool(abs(did_coef) >= 2.0 and ci_excl_zero)

print(f"\n{'='*60}")
print("TWFE DiD RESULTS")
print("="*60)
print(f"  DiD Coefficient  : {did_coef:+.3f} pp")
print(f"  95% CI           : [{ci_lower:.3f}, {ci_upper:.3f}]")
print(f"  P-value          : {p_value:.4f}")
print(f"  CI excludes zero : {ci_excl_zero}")
print(f"  |coef| >= 2.0 pp : {abs(did_coef) >= 2.0}")
print(f"  PASSED           : {passed}")

# ============================================================
# WRITE OUTPUTS
# ============================================================

baseline_metric = {
    "metric_name":        "naive_did_pp",
    "description":        ("Unadjusted DiD — 2x2 weighted means, no controls, no FE. "
                           "Treatment = states below NFHS-4 median (PMUY-targeted)."),
    "treatment_pre_pp":   round(treat_pre,              2),
    "treatment_post_pp":  round(treat_post,             2),
    "treatment_delta_pp": round(treat_post - treat_pre, 2),
    "control_pre_pp":     round(ctrl_pre,               2),
    "control_post_pp":    round(ctrl_post,              2),
    "control_delta_pp":   round(ctrl_post - ctrl_pre,   2),
    "value":              round(naive_did,              2),
    "unit":               "percentage points",
    "threshold":          2.0,
     
}
with open("outputs/baseline_metric.json", "w") as f:
    json.dump(baseline_metric, f, indent=2)
print("\n✓ Wrote outputs/baseline_metric.json")

ci_excludes_zero = (ci_lower > 0 and ci_upper > 0) or \
                   (ci_lower < 0 and ci_upper < 0)
# --- primary_metric.json  ---
primary_metric = {
    "metric_name": "did_coefficient_pp",
    "value": round(did_coef, 3),
    "ci_lower": round(ci_lower, 3),
    "ci_upper": round(ci_upper, 3),
    "p_value": round(p_value, 4),
    "threshold": "|value| >= 2.0 pp AND CI excludes zero",
    "passed": bool(ci_excludes_zero  and abs(did_coef) >= 2.0 ),
    "unit": "percentage points",
    "status": "computed_twfe_with_state_trends",
    "notes": "TWFE coefficient with state FE, time FE, state-specific linear trends (θ_s·t), controls, and state-clustered SEs",
    "specification": "clean_fuel ~ post + high_exposure + did_interaction + C(state) + C(state):post + controls"
}

with open("outputs/primary_metric.json", "w") as f:
    json.dump(primary_metric, f, indent=2)
print("✓ Wrote outputs/primary_metric.json (with TWFE results)")

with open("outputs/primary_metric.json", "w") as f:
    json.dump(primary_metric, f, indent=2)
print("✓ Wrote outputs/primary_metric.json")

milestone_manifest = {
    "milestone_date":  "2026-05-07",
    "project":         "The Impact of PMUY on Clean Fuel Adoption: A DiD Analysis Using NFHS-4 and NFHS-5",
    "team":            ["Tanisha Aggarwal", "Neha Rana", "Jaswathi Lalitha R"],
    "charter_locked":  True,
    "status":          "milestone",
    "sources": [{
        "name":                  "pmuy_data_compressed.csv.gz",
        "file":                  "data/pmuy_data_compressed.csv.gz",
        "rows_after_exclusions": int(len(df)),
        "states":                int(df["state"].nunique()),
        "status":                "verified",
        "probe_artifact":        "artifacts/probes/probe_nfhs.md",
        "note":                  "Compressed CSV stored in data/. No external download required.",
    }],
    "treatment_definition": {
        "variable":           "high_exposure",
        "direction":          "1 = LOW clean-fuel-access states (below NFHS-4 median) = PMUY-targeted",
        "nfhs4_median_pp":    round(median_value, 1),
        "n_treatment_states": int(len(high_exp_states)),
        "n_control_states":   int(len(low_exp_states)),
        "treatment_states":   sorted(high_exp_states),
        "control_states":     sorted(low_exp_states),
    },
    "success_threshold": {
        "rule":      "|did_coefficient_pp| >= 2.0 AND CI excludes zero",
        "threshold": 2.0,
    },
    "baseline_ready":              True,
    "primary_metric_schema_ready": True,
    "baseline_metric": {"file": "outputs/baseline_metric.json", "value_pp": round(naive_did,2), "status": "written"},
    "primary_metric":  {"file": "outputs/primary_metric.json",  "value_pp": round(did_coef,3), "passed": passed, "status": "written"},
    "run_command": "uv run main.py",
}
with open("outputs/milestone_manifest.json", "w") as f:
    json.dump(milestone_manifest, f, indent=2)
print("✓ Wrote outputs/milestone_manifest.json")

print("\n" + "="*60)
print("MILESTONE COMPLETE")
print("="*60)
print(f"  Naive DiD  : {naive_did:+.1f} pp")
print(f"  TWFE DiD   : {did_coef:+.3f} pp  CI [{ci_lower:.3f}, {ci_upper:.3f}]")
print(f"  Passed     : {passed}")

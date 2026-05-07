 #!/usr/bin/env python3
"""
PMUY Clean Fuel Adoption Analysis - Milestone Pipeline
ECO 6810 Final Project
Stops at naive DiD. TWFE regression is placeholder for final submission.
"""

import json
import os
import numpy as np
import pandas as pd
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)

print("=" * 80)
print("PMUY CLEAN FUEL ADOPTION ANALYSIS — MILESTONE")
print("=" * 80)

# ============================================================
# DOWNLOAD DATA
# ============================================================

FILE_ID     = "1V94LK_vh0R-D3Hioa5J8hqzenECcuyCZ"
OUTPUT_FILE = "pmuy_data.csv"

if not os.path.exists(OUTPUT_FILE):
    try:
        import gdown
    except ImportError:
        os.system("pip install gdown -q")
        import gdown
    print(f"Downloading {OUTPUT_FILE}...")
    gdown.download(f"https://drive.google.com/uc?id={FILE_ID}", OUTPUT_FILE, quiet=False)
    print("✓ Download complete")
else:
    print(f"✓ Found existing {OUTPUT_FILE}")

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(OUTPUT_FILE)
print(f"✓ Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")
print(f"  Columns: {df.columns.tolist()}")

# ============================================================
# STEP 1: WEIGHTS
# ============================================================

if 'hv005' in df.columns:
    df['weight'] = df['hv005'] / 1_000_000
    print(f"\n✓ DHS weights created (hv005 / 1,000,000)")
    print(f"  Weight range: {df['weight'].min():.4f} — {df['weight'].max():.4f}")
else:
    df['weight'] = 1.0
    print("\n⚠ hv005 not found — using equal weights")

# ============================================================
# STEP 2: CLEAN FUEL BINARY
# Use str.contains to handle label differences across rounds
# e.g. NFHS-4 uses 'lpg, natural gas', NFHS-5 may use 'lpg'
# ============================================================

print("\n=== hv226 raw labels by survey round ===")
print(df.groupby('survey')['hv226'].value_counts().to_string())

def is_clean_fuel(val):
    if pd.isna(val):
        return np.nan
    v = str(val).lower().strip()
    if v in ['no food cooked in house', 'other', 'nan']:
        return np.nan
    if 'electricity' in v:
        return 1
    if 'lpg' in v or 'natural gas' in v:
        return 1
    if 'biogas' in v:
        return 1
    return 0

df['clean_fuel'] = df['hv226'].apply(is_clean_fuel)
df = df[df['clean_fuel'].notna()].copy()
df['clean_fuel'] = df['clean_fuel'].astype(int)

# Verify rates look correct by round
print("\n=== Clean fuel rate by round (weighted) ===")
for rnd in sorted(df['survey'].unique()):
    sub  = df[df['survey'] == rnd]
    rate = np.average(sub['clean_fuel'], weights=sub['weight']) * 100
    print(f"  NFHS-{rnd}: {rate:.1f}%  (n={len(sub):,})")
print("  Expected: NFHS-4 ~40-45%, NFHS-5 ~55-60%")

overall = np.average(df['clean_fuel'], weights=df['weight']) * 100
print(f"  Overall (both rounds): {overall:.1f}%")

# ============================================================
# STEP 3: STANDARDISE STATE NAMES
# ============================================================

df['state'] = df['hv024'].astype(str).str.lower().str.strip()

# State consistency check
states_4 = set(df[df['post'] == 0]['state'].unique())
states_5 = set(df[df['post'] == 1]['state'].unique())
print(f"\n✓ States in NFHS-4: {len(states_4)}")
print(f"✓ States in NFHS-5: {len(states_5)}")
only_4 = states_4 - states_5
only_5 = states_5 - states_4
if only_4:
    print(f"⚠ Only in NFHS-4: {sorted(only_4)}")
if only_5:
    print(f"⚠ Only in NFHS-5: {sorted(only_5)}")
if not only_4 and not only_5:
    print("✓ All states present in both rounds")

# ============================================================
# STEP 4: BINARY CONTROL VARIABLES
# ============================================================

print("\n" + "=" * 60)
print("CREATING BINARY CONTROL VARIABLES")
print("=" * 60)

# Rural
if 'hv025' in df.columns:
    df['rural'] = df['hv025'].str.lower().str.strip().map(
        {'rural': 1, 'urban': 0}).fillna(0).astype(int)
    print(f"✓ rural           — mean: {df['rural'].mean()*100:.1f}%")

# Electricity
if 'hv206' in df.columns:
    df['electricity'] = df['hv206'].str.lower().str.strip().map(
        {'yes': 1, 'no': 0}).fillna(0).astype(int)
    print(f"✓ electricity     — mean: {df['electricity'].mean()*100:.1f}%")

# Female head
if 'hv219' in df.columns:
    df['female_head'] = df['hv219'].str.lower().str.strip().map(
        {'female': 1, 'male': 0}).fillna(0).astype(int)
    print(f"✓ female_head     — mean: {df['female_head'].mean()*100:.1f}%")

# Improved water
if 'hv201' in df.columns:
    improved_sources = [
        'piped into dwelling', 'piped to yard/plot', 'public tap/standpipe',
        'tube well or borehole', 'protected well', 'protected spring',
        'rainwater', 'bottled water'
    ]
    df['improved_water'] = df['hv201'].str.lower().str.strip().isin(
        improved_sources).astype(int)
    print(f"✓ improved_water  — mean: {df['improved_water'].mean()*100:.1f}%")

# Piped water
if 'hv201' in df.columns:
    df['piped_water'] = df['hv201'].str.lower().str.strip().isin(
        ['piped into dwelling', 'piped to yard/plot']).astype(int)
    print(f"✓ piped_water     — mean: {df['piped_water'].mean()*100:.1f}%")

# Improved floor
if 'hv213' in df.columns:
    unimproved = ['mud/clay/earth', 'dung', 'sand',
                  'raw wood planks', 'palm, bamboo', 'stone']
    df['improved_floor'] = (~df['hv213'].str.lower().str.strip().isin(
        unimproved)).astype(int)
    print(f"✓ improved_floor  — mean: {df['improved_floor'].mean()*100:.1f}%")

# Wealth quintile + rich dummy
if 'hv270' in df.columns:
    wealth_map = {'poorest': 1, 'poorer': 2, 'middle': 3,
                  'richer': 4, 'richest': 5}
    df['wealth_quintile'] = df['hv270'].astype(str).str.lower().map(wealth_map)
    df['rich'] = (df['wealth_quintile'] >= 4).astype(int)
    print(f"✓ wealth_quintile — mean: {df['wealth_quintile'].mean():.2f}")
    print(f"✓ rich (Q4-Q5)    — mean: {df['rich'].mean()*100:.1f}%")

# Head education
if 'hv106_01' in df.columns:
    df['head_edu'] = df['hv106_01'].str.lower().str.strip()
    df['head_higher_edu'] = df['head_edu'].isin(
        ['secondary', 'higher']).astype(int)
    print(f"✓ head_higher_edu — mean: {df['head_higher_edu'].mean()*100:.1f}%")

# Caste dummies (missing → 'not stated')
if 'sh36' in df.columns:
    df['caste'] = df['sh36'].fillna('not stated').str.lower().str.strip()
    for cat, col in [('scheduled caste',    'caste_sc'),
                     ('scheduled tribe',    'caste_st'),
                     ('other backward class', 'caste_obc'),
                     ('none of above',       'caste_general')]:
        df[col] = (df['caste'] == cat).astype(int)
    print(f"✓ caste dummies   — SC/ST/OBC/General created "
          f"(missing filled as 'not stated')")

# Religion dummies
if 'sh34' in df.columns:
    df['religion'] = df['sh34'].str.lower().str.strip()
    for rel, col in [('hindu',    'rel_hindu'),
                     ('muslim',   'rel_muslim'),
                     ('christian','rel_christian'),
                     ('sikh',     'rel_sikh')]:
        df[col] = (df['religion'] == rel).astype(int)
    print(f"✓ religion dummies — Hindu/Muslim/Christian/Sikh created")

# ============================================================
# STEP 5: TREATMENT DEFINITION
# high_exposure = 1 → BELOW median NFHS-4 clean fuel
# = high solid fuel dependence = PMUY primary targets
# Confirmed: PMUY targeted UP, Bihar, WB, MP, Odisha (low LPG states)
# ============================================================

print("\n" + "=" * 60)
print("TREATMENT DEFINITION")
print("=" * 60)

state_nfhs4 = (
    df[df['post'] == 0]
    .groupby('state')
    .apply(lambda x: np.average(x['clean_fuel'], weights=x['weight']) * 100,
           include_groups=False)
    .sort_values()
)

median_value = float(state_nfhs4.median())
high_exp_states = state_nfhs4[state_nfhs4 <  median_value].index.tolist()
low_exp_states  = state_nfhs4[state_nfhs4 >= median_value].index.tolist()

df['high_exposure'] = df['state'].isin(high_exp_states).astype(int)
df['post_x_high']   = df['post'] * df['high_exposure']

print(f"\nNFHS-4 clean fuel share by state (sorted):")
for s, v in state_nfhs4.items():
    tag = " ← TREATMENT" if s in high_exp_states else ""
    print(f"  {s:40s}: {v:.1f}%{tag}")

print(f"\nMedian: {median_value:.1f}%")
print(f"Treatment states (high_exposure=1, low baseline, PMUY targets): "
      f"{len(high_exp_states)}")
print(sorted(high_exp_states))
print(f"Control states (high_exposure=0, high baseline): {len(low_exp_states)}")
print(sorted(low_exp_states))

# ============================================================
# STEP 6: NAIVE DiD (BASELINE METRIC)
# ============================================================

def wmean(sub):
    return float(np.average(sub['clean_fuel'], weights=sub['weight']) * 100)

treat_pre  = wmean(df[(df['high_exposure'] == 1) & (df['post'] == 0)])
treat_post = wmean(df[(df['high_exposure'] == 1) & (df['post'] == 1)])
ctrl_pre   = wmean(df[(df['high_exposure'] == 0) & (df['post'] == 0)])
ctrl_post  = wmean(df[(df['high_exposure'] == 0) & (df['post'] == 1)])
naive_did  = (treat_post - treat_pre) - (ctrl_post - ctrl_pre)

print(f"\n{'='*60}")
print("NAIVE DiD — 2×2 WEIGHTED MEANS (No controls, no FE)")
print("="*60)
print(f"  Treatment (low baseline): {treat_pre:.1f}% → {treat_post:.1f}%  "
      f"Δ = {treat_post - treat_pre:+.1f} pp")
print(f"  Control (high baseline):  {ctrl_pre:.1f}% → {ctrl_post:.1f}%  "
      f"Δ = {ctrl_post - ctrl_pre:+.1f} pp")
print(f"  Naive DiD:  {naive_did:+.1f} pp")
print(f"  Expected sign: POSITIVE (treatment states caught up more)")

# ============================================================
# STEP 7: SUMMARY STATISTICS TABLE
# ============================================================

print("\n" + "="*80)
print("SUMMARY STATISTICS — RAW WEIGHTED MEANS BY GROUP × PERIOD")
print("="*80)

groups = [
    ('Pre-Treatment',  0, 1),
    ('Pre-Control',    0, 0),
    ('Post-Treatment', 1, 1),
    ('Post-Control',   1, 0),
]

stat_vars = {
    'Clean Fuel (0/1)'       : 'clean_fuel',
    'Rural (0/1)'            : 'rural',
    'Electricity (0/1)'      : 'electricity',
    'Wealth Quintile (1-5)'  : 'wealth_quintile',
    'Rich Q4-Q5 (0/1)'       : 'rich',
    'Female Head (0/1)'      : 'female_head',
    'Head Higher Edu (0/1)'  : 'head_higher_edu',
    'Improved Water (0/1)'   : 'improved_water',
    'Improved Floor (0/1)'   : 'improved_floor',
    'Piped Water (0/1)'      : 'piped_water',
}

rows = []
for label, var_col in stat_vars.items():
    if var_col not in df.columns:
        continue
    row = {'Variable': label}
    for grp_label, post_val, treat_val in groups:
        sub = df[(df['post'] == post_val) & (df['high_exposure'] == treat_val)]
        vals = pd.to_numeric(sub[var_col], errors='coerce').dropna()
        wts  = sub.loc[vals.index, 'weight']
        if len(vals) > 0:
            m = float(np.average(vals, weights=wts))
            s = float(np.sqrt(np.average((vals - m)**2, weights=wts)))
            row[grp_label] = f"{m:.3f} ± {s:.3f}"
        else:
            row[grp_label] = 'N/A'
    rows.append(row)

# Observation counts
obs_row = {'Variable': 'Observations (N)'}
for grp_label, post_val, treat_val in groups:
    n = len(df[(df['post'] == post_val) & (df['high_exposure'] == treat_val)])
    obs_row[grp_label] = f"{n:,}"
rows.append(obs_row)

summary_df = pd.DataFrame(rows)
print(summary_df.to_string(index=False))

# ============================================================
# STEP 8: SAVE OUTPUTS
# ============================================================

# Baseline metric
baseline_metric = {
    "metric_name"        : "naive_did_pp",
    "description"        : "Unadjusted DiD — 2x2 weighted means, no controls, no FE.",
    "treatment_pre_pp"   : round(treat_pre,  2),
    "treatment_post_pp"  : round(treat_post, 2),
    "treatment_delta_pp" : round(treat_post - treat_pre, 2),
    "control_pre_pp"     : round(ctrl_pre,  2),
    "control_post_pp"    : round(ctrl_post, 2),
    "control_delta_pp"   : round(ctrl_post - ctrl_pre, 2),
    "value"              : round(naive_did, 2),
    "unit"               : "percentage points",
    "threshold"          : 3.0,
    "passed"             : bool(naive_did >= 3.0),
}

with open('outputs/baseline_metric.json', 'w') as f:
    json.dump(baseline_metric, f, indent=2)
print("\n✓ Wrote outputs/baseline_metric.json")

# Primary metric — placeholder for final submission
primary_metric = {
    "metric_name"  : "did_coefficient_pp",
    "value"        : None,
    "ci_lower"     : None,
    "ci_upper"     : None,
    "p_value"      : None,
    "threshold"    : 3.0,
    "passed"       : None,
    "unit"         : "percentage points",
    "notes"        : ("Placeholder. TWFE coefficient with state FE, time FE, "
                      "controls, and state-clustered SEs to be computed "
                      "in final submission via uv run main.py"),
    "is_template"  : True,
}

with open('outputs/primary_metric.json', 'w') as f:
    json.dump(primary_metric, f, indent=2)
print("✓ Wrote outputs/primary_metric.json (placeholder)")

# Milestone manifest
milestone_manifest = {
    "milestone_date"   : "2026-05-07",
    "project"          : ("The Impact of PMUY on Clean Fuel Adoption: "
                          "A Difference-in-Differences Analysis Using NFHS-4 and NFHS-5"),
    "team"             : ["Tanisha Aggarwal", "Neha Rana", "Jaswathi Lalitha R"],
    "charter_locked"   : True,
    "status"           : "milestone",
    "sources"          : [{
        "name"   : "pmuy_data.csv",
        "file_id": FILE_ID,
        "rows_after_exclusions": int(len(df)),
        "states" : int(df['state'].nunique()),
        "status" : "verified",
    }],
    "treatment_definition" : {
        "variable"          : "high_exposure",
        "direction"         : "1 = LOW-access states (below NFHS-4 median) = PMUY-targeted",
        "nfhs4_median_pp"   : round(median_value, 1),
        "n_treatment_states": int(len(high_exp_states)),
        "n_control_states"  : int(len(low_exp_states)),
        "treatment_states"  : sorted(high_exp_states),
        "control_states"    : sorted(low_exp_states),
    },
    "baseline_ready"   : True,
    "baseline_metric"  : {
        "file"     : "outputs/baseline_metric.json",
        "value_pp" : round(naive_did, 2),
        "status"   : "written",
    },
    "primary_metric_schema_ready": False,
    "completed" : [
        "NFHS-4+5 panel loaded and verified",
        f"clean_fuel outcome constructed from hv226 ({int(df['clean_fuel'].sum()):,} clean households)",
        "Binary controls created: rural, electricity, female_head, improved_water, "
        "improved_floor, piped_water, rich, head_higher_edu",
        "Caste dummies: SC, ST, OBC, General (missing → not stated)",
        "Religion dummies: Hindu, Muslim, Christian, Sikh",
        f"Treatment defined: high_exposure=1 for {len(high_exp_states)} states "
        f"below NFHS-4 median ({median_value:.1f}%)",
        f"Naive DiD baseline: {naive_did:+.1f} pp written to outputs/baseline_metric.json",
    ],
    "remaining_for_final" : [
        "TWFE regression → outputs/primary_metric.json",
        "State-clustered standard errors",
        "Parallel trends event-study plot",
        "Continuous treatment robustness spec (Risk 2 in charter)",
        "report.md with results tables",
        "AI_USAGE_LOG.md",
    ],
    "run_command": "uv run main.py",
}

with open('outputs/milestone_manifest.json', 'w') as f:
    json.dump(milestone_manifest, f, indent=2)
print("✓ Wrote outputs/milestone_manifest.json")

print("\n" + "=" * 60)
print("MILESTONE COMPLETE")
print("=" * 60)
print(f"  Naive DiD           : {naive_did:+.1f} pp")
print(f"  Treatment states    : {len(high_exp_states)}")
print(f"  Control states      : {len(low_exp_states)}")
print(f"  Total observations  : {len(df):,}")
print(f"  NFHS-4 observations : {len(df[df['post']==0]):,}")
print(f"  NFHS-5 observations : {len(df[df['post']==1]):,}")
print("\n  Outputs written to outputs/")
print("  → baseline_metric.json ✓")
print("  → primary_metric.json  (placeholder) ✓")
print("  → milestone_manifest.json ✓")

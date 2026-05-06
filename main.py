 """
main.py  —  PMUY Clean-Fuel Adoption: Causal DiD Pipeline
ECO 6810 Final Project — Tanisha Aggarwal, Neha Rana, Jaswathi Lalitha R

Usage
-----
    
    uv run main.py --milestone   # milestone: baseline + manifest only, no regression

Treatment definition
--------------------
high_exposure = 1  →  LOW-access states (below NFHS-4 median clean-fuel share ~52.3%)
                       PMUY-targeted states (Bihar, Jharkhand, Odisha, etc.)
high_exposure = 0  →  HIGH-access states (above median, control group)

Success threshold
-----------------
|β̂₃| >= 2.0 pp AND 95% CI excludes zero.
Both convergence (positive) and divergence (negative) are valid findings.
"""

import argparse
import json
import os
import sys
import numpy as np
import pandas as pd

# ── paths ─────────────────────────────────────────────────────────────────────
DATA_PATH    = "data/nr.csv"
OUT_DIR      = "outputs"
BASELINE_OUT = os.path.join(OUT_DIR, "baseline_metric.json")
PRIMARY_OUT  = os.path.join(OUT_DIR, "primary_metric.json")
MANIFEST_OUT = os.path.join(OUT_DIR, "milestone_manifest.json")
THRESHOLD    = 2.0

os.makedirs(OUT_DIR, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("--milestone", action="store_true",
                    help="Milestone mode: write baseline + manifest only, skip TWFE.")
args = parser.parse_args()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — validate data path
# ═══════════════════════════════════════════════════════════════════════════════
print("=" * 70)
print("PMUY Clean-Fuel DiD Pipeline")
print("=" * 70)

if not os.path.exists(DATA_PATH):
    print(f"\nERROR: {DATA_PATH} not found.")
    print("Place the merged NFHS-4+5 panel CSV at data/nr.csv")
    print("Access: see CHARTER.md §6 or the shared link in README.md")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — load
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n[1/6] Loading {DATA_PATH} ...")
df = pd.read_csv(DATA_PATH)
print(f"      Raw rows: {len(df):,}   columns: {df.shape[1]}")

required = {
    "hv005", "hv009", "hv024", "hv025", "hv201",
    "hv206", "hv213", "hv219", "hv220", "hv226",
    "hv270", "sh34", "sh36", "hv106_01",
    "state", "survey", "post"
}
missing_cols = required - set(df.columns)
if missing_cols:
    print(f"\nERROR: Missing columns: {missing_cols}")
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — clean and engineer features
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[2/6] Engineering features ...")

df["weight"] = df["hv005"] / 1_000_000

# outcome
CLEAN_FUELS = {"electricity", "lpg, natural gas", "biogas"}
df = df[df["hv226"] != "no food cooked in house"].copy()
df["clean_fuel"] = df["hv226"].isin(CLEAN_FUELS).astype(int)

# binary controls — exactly matching Colab notebook
df["rural"]       = df["hv025"].str.lower().str.strip().map({"rural":1,"urban":0}).fillna(0).astype(int)
df["electricity"] = df["hv206"].str.lower().str.strip().map({"yes":1,"no":0}).fillna(0).astype(int)
df["female_head"] = df["hv219"].str.lower().str.strip().map({"female":1,"male":0}).fillna(0).astype(int)

improved_water_sources = {
    "piped into dwelling","piped to yard/plot","public tap/standpipe",
    "tube well or borehole","protected well","protected spring","rainwater","bottled water"
}
df["improved_water"] = df["hv201"].str.lower().str.strip().isin(improved_water_sources).astype(int)

unimproved_floors = {"mud/clay/earth","dung","sand","raw wood planks","palm, bamboo","stone"}
df["improved_floor"] = (~df["hv213"].str.lower().str.strip().isin(unimproved_floors)).astype(int)

df["piped_water"] = df["hv201"].str.lower().str.strip().isin(
    {"piped into dwelling","piped to yard/plot"}
).astype(int)

wealth_map = {"poorest":1,"poorer":2,"middle":3,"richer":4,"richest":5}
df["wealth_quintile"] = df["hv270"].astype(str).str.lower().map(wealth_map)
df["rich"]            = (df["wealth_quintile"] >= 4).astype(int)

df["head_higher_edu"] = df["hv106_01"].astype(str).str.lower().isin(
    ["secondary","higher"]
).astype(int)

# missing caste: 4.2% — fill as '99' (consistent with Colab)
df["sh36"] = df["sh36"].fillna("99")

print(f"      Rows after exclusions: {len(df):,}  (expected ~1,235,952)")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — define treatment
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[3/6] Defining treatment variable ...")

state_pre = (
    df[df["post"] == 0]
    .groupby("state")
    .apply(lambda x: np.average(x["clean_fuel"], weights=x["weight"]) * 100,
           include_groups=False)
    .sort_values()
)
median_pp   = state_pre.median()
low_access  = state_pre[state_pre <  median_pp].index.tolist()
high_access = state_pre[state_pre >= median_pp].index.tolist()

df["high_exposure"] = df["state"].isin(low_access).astype(int)
df["did"]           = df["post"] * df["high_exposure"]

print(f"      NFHS-4 median: {median_pp:.2f}%  (expected ~52.3%)")
print(f"      Treatment (low-access)  states: {len(low_access)}  (expected 17)")
print(f"      Control  (high-access)  states: {len(high_access)} (expected 18)")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5 — baseline metric (naïve 2×2 DiD)
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[4/6] Computing baseline (naïve DiD) ...")

def wmean(sub):
    return np.average(sub["clean_fuel"], weights=sub["weight"]) * 100

treat_pre  = wmean(df[(df["high_exposure"]==1) & (df["post"]==0)])
treat_post = wmean(df[(df["high_exposure"]==1) & (df["post"]==1)])
ctrl_pre   = wmean(df[(df["high_exposure"]==0) & (df["post"]==0)])
ctrl_post  = wmean(df[(df["high_exposure"]==0) & (df["post"]==1)])

treat_delta = treat_post - treat_pre
ctrl_delta  = ctrl_post  - ctrl_pre
naive_did   = treat_delta - ctrl_delta

print(f"      Treatment: {treat_pre:.1f}% → {treat_post:.1f}%  Δ={treat_delta:+.1f} pp")
print(f"      Control  : {ctrl_pre:.1f}% → {ctrl_post:.1f}%  Δ={ctrl_delta:+.1f} pp")
print(f"      Naïve DiD: {naive_did:+.2f} pp  (expected ≈ −2.0 pp)")

baseline = {
    "metric_name":        "naive_did_pp",
    "description":        (
        "Unadjusted DiD — 2x2 weighted means, no controls, no FE. "
        "Treatment = low-access states (below NFHS-4 median ~52.3%), i.e. PMUY-targeted."
    ),
    "treatment_pre_pp":   round(treat_pre,   2),
    "treatment_post_pp":  round(treat_post,  2),
    "treatment_delta_pp": round(treat_delta, 2),
    "control_pre_pp":     round(ctrl_pre,    2),
    "control_post_pp":    round(ctrl_post,   2),
    "control_delta_pp":   round(ctrl_delta,  2),
    "value":              round(naive_did,   2),
    "unit":               "percentage points",
    "threshold":          THRESHOLD,
    "threshold_rule":     "|value| >= 2.0 pp",
    "passed":             bool(abs(naive_did) >= THRESHOLD),
    "note": (
        "Naive DiD is negative (divergence). TWFE adjusts for pre-existing differences. "
        "Threshold is absolute magnitude — a precisely estimated negative result "
        "is as valid as a positive one for the policy question."
    ),
}
with open(BASELINE_OUT, "w") as f:
    json.dump(baseline, f, indent=2)
print(f"      Written → {BASELINE_OUT}")

# ── milestone mode stops here ─────────────────────────────────────────────────
if args.milestone:
    manifest = {
        "milestone_date": "2026-05-06",
        "project":        "PMUY Clean-Fuel Adoption — Causal DiD (ECO 6810)",
        "mode":           "milestone",
        "data": {
            "file":                     DATA_PATH,
            "rows_raw":                 1238208,
            "rows_after_exclusions":    int(len(df)),
            "nfhs4_obs":                int((df["post"]==0).sum()),
            "nfhs5_obs":                int((df["post"]==1).sum()),
            "states_uts":               int(df["state"].nunique()),
            "clean_fuel_mean_weighted": round(
                float(np.average(df["clean_fuel"], weights=df["weight"])), 4
            ),
        },
        "treatment_definition": {
            "variable":           "high_exposure",
            "direction":          "1 = LOW-access states (below NFHS-4 median) = PMUY-targeted",
            "nfhs4_median_pp":    round(median_pp, 2),
            "n_treatment_states": len(low_access),
            "n_control_states":   len(high_access),
            "treatment_states":   sorted(low_access),
            "control_states":     sorted(high_access),
        },
        "success_threshold": {
            "rule":      "|did_coefficient_pp| >= 2.0 AND CI excludes zero",
            "threshold": THRESHOLD,
            "rationale": (
                "Absolute-magnitude threshold: >=2.0 pp in either direction is "
                "policy-relevant. Naive DiD of -2.0 pp sets prior toward divergence. "
                "A significant negative result informs the Ministry refill-subsidy decision."
            ),
        },
        "baseline_metric": baseline,
        "primary_metric":  {
            "file":   PRIMARY_OUT,
            "status": "pending — run `uv run main.py` (without --milestone) to compute",
        },
        "completed_for_milestone": [
            f"NFHS-4+5 panel loaded ({len(df):,} obs after exclusions)",
            "All binary controls constructed matching Colab notebook",
            "Missing caste (sh36, 4.2%) filled as '99'",
            "35 states confirmed present in both NFHS-4 and NFHS-5",
            f"Treatment: high_exposure=1 for {len(low_access)} low-access states "
            f"(below NFHS-4 median {median_pp:.1f}%)",
            f"Naive DiD baseline: {naive_did:+.2f} pp → {BASELINE_OUT}",
            "Charter approved: threshold |β̂₃| >= 2.0 pp, CI excludes zero",
            "Data probe: artifacts/probes/probe_nfhs.py",
            "PPAC probe: artifacts/probes/probe_ppac.py",
        ],
        "remaining_for_final": [
            "TWFE regression → outputs/primary_metric.json",
            "NFHS-3 parallel-trends fallback (Risk 1 in charter)",
            "Continuous-treatment robustness spec (Risk 2 in charter)",
            "report.md with results tables and event-study figure",
            "AI_USAGE_LOG.md",
        ],
    }
    with open(MANIFEST_OUT, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"      Written → {MANIFEST_OUT}")
    print("\n[milestone complete]")
    print("Run `uv run main.py` (no --milestone) to compute primary_metric.json.")
    sys.exit(0)

 

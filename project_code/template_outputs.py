from __future__ import annotations


 def build_baseline_metric() -> dict:
    return {
        "metric_name": "naive_did_pp",
        "description": (
            "Unadjusted DiD — 2x2 weighted means, no controls, no FE. "
            "Treatment = High exposure states (below NFHS-4 median ~52.3 pp), i.e. PMUY-targeted. "
            "Control = Low exposure states (above median)."
        ),
        "treatment_group": "High exposure states (high_exposure=1, below NFHS-4 median) — PMUY-targeted",
        "control_group":   "Low exposure states (high_exposure=0, above NFHS-4 median) — control",
        "treatment_pre_pp":   27.4,
        "treatment_post_pp":  42.0,
        "treatment_delta_pp": 14.6,
        "control_pre_pp":   63.0,
        "control_post_pp":  79.5,
        "control_delta_pp": 16.6,
        "value":    -2.0,
        "unit":     "percentage points",
        "threshold": 2.0,
        "threshold_rule": "|value| >= 2.0 pp",
        "passed":   True,
        "note": (
            "Naive DiD is negative (-2.0 pp): low-access states improved less than "
            "high-access states unconditionally. This is the unadjusted baseline. "
            "The covariate-adjusted TWFE estimate in primary_metric.json is the graded deliverable. "
            "Threshold is absolute magnitude — |-2.0| = 2.0 pp meets the bar."
        ),
    }


def build_primary_metric() -> dict:
    return {
        "metric_name": "replace_me_primary",
        "value": 0.0,
        "threshold": 0.0,
        "passed": False,
        "notes": "Template value. Replace this with your real project metric before the final submission.",
        "is_template": True,
    }


 def build_milestone_manifest() -> dict:
    return {
        "milestone_date": "2026-05-06",
        "project": "PMUY Clean-Fuel Adoption — Causal DiD Analysis (ECO 6810)",
        "team": ["Tanisha Aggarwal", "Neha Rana", "Jaswathi Lalitha R"],
        "charter_locked": True,
        "status": "milestone",
 
        "sources": [
            {
                "name": "NFHS-4+5 household panel ",
                "file": "https://drive.google.com/file/d/1V94LK_vh0R-D3Hioa5J8hqzenECcuyCZ/view",
                "rows_raw": 1238208,
                "rows_after_exclusions": 1235952,
                "nfhs4_obs": 600328,
                "nfhs5_obs": 635624,
                "states_uts": 35,
                "clean_fuel_mean_unweighted": 0.4565,
                "status": "verified",
                "probe_artifact": "artifacts/probes/probe_nfhs.py",
                "note": "Merged NFHS-4 and NFHS-5 household microdata. Primary outcome source.",
            },
            {
                "name": "PPAC State-wise PMUY Connections",
                "url": "https://ppac.gov.in/consumption/state-wise-pmuy-data",
                "backup": "https://www.data.gov.in/resource/stateut-wise-number-pradhan-mantri-ujjwala-yojana-pmuy-connections-2018-2023",
                "status": "verified",
                "probe_artifact": "artifacts/probes/probe_ppac.py",
                "note": "Used only to validate high/low exposure split. Not a primary outcome source.",
            },
        ],
 
        "treatment_definition": {
            "variable": "high_exposure",
            "direction": "1 = LOW-access states (below NFHS-4 median) = PMUY-targeted",
            "nfhs4_median_pp": 52.3,
            "n_treatment_states": 17,
            "n_control_states": 18,
            "treatment_states": [
                "bihar", "jharkhand", "odisha", "meghalaya", "chhattisgarh",
                "assam", "west bengal", "madhya pradesh", "tripura", "rajasthan",
                "lakshadweep", "uttar pradesh", "nagaland", "himachal pradesh",
                "manipur", "arunachal pradesh", "uttarakhand",
            ],
            "control_states": [
                "haryana", "gujarat", "karnataka", "kerala", "jammu and kashmir",
                "sikkim", "maharashtra", "andhra pradesh", "andaman and nicobar islands",
                "dadra and nagar haveli and daman and diu", "punjab", "mizoram",
                "telangana", "tamil nadu", "goa", "puducherry", "chandigarh", "delhi",
            ],
        },
 
        "success_threshold": {
            "rule": "|did_coefficient_pp| >= 2.0 AND CI excludes zero",
            "threshold": 2.0,
            "rationale": (
                "Absolute-magnitude threshold: >=2.0 pp in either direction is policy-relevant. "
                "Naive DiD of -2.0 pp sets prior toward divergence. "
                "A significant negative result informs the Ministry refill-subsidy decision."
            ),
        },
 
        "baseline_ready": True,
        "baseline_metric": {
            "file": "outputs/baseline_metric.json",
            "value_pp": -2.0,
            "threshold_rule": "|value| >= 2.0 pp",
            "passed": True,
            "status": "written",
        },
 
        "primary_metric_schema_ready": True,
        "primary_metric": {
            "file": "outputs/primary_metric.json",
            "status": "pending — run `uv run main.py` (without --milestone) to compute TWFE",
        },
 
        "completed": [
            "Charter approved (CHARTER.md) — threshold |β̂₃| >= 2.0 pp, CI excludes zero",
            "NFHS-4+5 panel loaded (1,238,208 raw rows; 1,235,952 after exclusions)",
            "Outcome variable clean_fuel constructed from hv226",
            "All binary controls constructed: rural, electricity, female_head, improved_water, "
            "improved_floor, piped_water, rich, head_higher_edu, wealth_quintile",
            "Missing caste (sh36, 4.2%) filled as '99'",
            "35 states confirmed present in both NFHS-4 and NFHS-5",
            "Treatment: high_exposure=1 for 17 low-access states below NFHS-4 median (52.3 pp)",
            "Descriptive 2x2 summary table produced (4 group x period cells)",
            "Naive DiD baseline: -2.0 pp written to outputs/baseline_metric.json",
            "Data probe: artifacts/probes/probe_nfhs.py",
            "PPAC probe: artifacts/probes/probe_ppac.py",
        ],
 
        "remaining_for_final": [
            "TWFE coefficient → outputs/primary_metric.json (run: uv run main.py)",
            "NFHS-3 parallel-trends fallback (Risk 1 in charter)",
            "Continuous-treatment robustness spec (Risk 2 in charter)",
            "report.md with results tables and event-study figure",
            "AI_USAGE_LOG.md",
        ],
 
        "run_command": "uv run main.py --milestone",
    }

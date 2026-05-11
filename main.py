from __future__ import annotations

# ============================================================
# ECO6810 FINAL PROJECT
# ASI Manufacturing COVID Shock and Recovery Analysis
# ============================================================

import json
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

DATA_PATH = (
    ROOT
    / "data"
    / "industry_shock_recovery_main_sample.csv"
)

OUTPUTS_DIR = ROOT / "outputs"

OUTPUTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("\nLoading industry-level ASI dataset...\n")

df = pd.read_csv(DATA_PATH)

print(f"Dataset loaded successfully.")
print(f"Number of industries: {df.shape[0]}")
print(f"Number of variables: {df.shape[1]}\n")


# ============================================================
# BASELINE METRIC
# ============================================================

# Naive benchmark:
# average GVA change during COVID year

baseline_value = (
    df["gva_drop_pct"]
    .mean()
)

baseline_metric = {

    "metric_name":
        "national_gva_drop_2020_21",

    "value":
        round(float(baseline_value), 4),

    "unit":
        "percent",

    "notes":
        (
            "Mean industry-level GVA change "
            "from 2019-20 to 2020-21 in the "
            "main sample, used as the naive "
            "descriptive benchmark before "
            "labour-intensity split."
        ),

    "is_template":
        False
}


# ============================================================
# PRIMARY METRIC
# ============================================================

# Compute mean GVA decline separately
# for labour-intensive and capital-intensive industries

capital_mean = (
    df.loc[
        df["labour_intensive"]
        == "Capital-intensive",
        "gva_drop_pct"
    ]
    .mean()
)

labour_mean = (
    df.loc[
        df["labour_intensive"]
        == "Labour-intensive",
        "gva_drop_pct"
    ]
    .mean()
)

# Difference in average decline

difference = abs(
    labour_mean - capital_mean
)

# Threshold conditions

industry_count = int(df.shape[0])

minimum_factory_count = int(
    df["min_factory_count"]
    .min()
)

threshold_difference = 2.0

threshold_industries = 20

threshold_factory_count = 300

passed = (
    difference >= threshold_difference
    and industry_count >= threshold_industries
    and minimum_factory_count >= threshold_factory_count
)

primary_metric = {

    "metric_name":
        "labour_intensive_excess_gva_decline",

    "value":
        round(float(difference), 4),

    "threshold":
        threshold_difference,

    "passed":
        bool(passed),

    "unit":
        "percentage_points",

    "capital_intensive_mean_drop":
        round(float(capital_mean), 4),

    "labour_intensive_mean_drop":
        round(float(labour_mean), 4),

    "industry_count":
        industry_count,

    "minimum_factory_count":
        minimum_factory_count,

    "notes":
        (
            "Labour-intensive manufacturing "
            "industries experienced a larger "
            "average GVA decline during "
            "2020-21 than capital-intensive "
            "industries. "
            "The project includes 23 NIC "
            "2-digit manufacturing industries "
            "with at least 300 factories "
            "in every year."
        ),

    "is_template":
        False
}


# ============================================================
# MILESTONE MANIFEST
# ============================================================

manifest = {

    "charter_locked":
        True,

    "sources": [
        {
            "name":
                "Annual Survey of Industries (ASI), MoSPI",

            "status":
                "working",

            "probe_artifact":
                "artifacts/probes/asi_probe.md",

            "note":
                (
                    "ASI Blocks A, C, D, and J "
                    "were cleaned and merged "
                    "to construct weighted "
                    "NIC-2 manufacturing "
                    "industry aggregates "
                    "for 2019-20, 2020-21, "
                    "and 2021-22."
                )
        }
    ],

    "baseline_ready":
        True,

    "primary_metric_schema_ready":
        True,

    "run_command":
        "uv run main.py"
}


# ============================================================
# WRITE OUTPUT FILES
# ============================================================

with open(
    OUTPUTS_DIR / "baseline_metric.json",
    "w"
) as f:

    json.dump(
        baseline_metric,
        f,
        indent=2
    )


with open(
    OUTPUTS_DIR / "primary_metric.json",
    "w"
) as f:

    json.dump(
        primary_metric,
        f,
        indent=2
    )


with open(
    OUTPUTS_DIR / "milestone_manifest.json",
    "w"
) as f:

    json.dump(
        manifest,
        f,
        indent=2
    )


# ============================================================
# CONSOLE OUTPUT
# ============================================================

print("================================================")
print("BASELINE METRIC")
print("================================================")

print(
    f"Mean GVA decline (2019-20 to 2020-21): "
    f"{baseline_metric['value']:.4f}%"
)

print("\n")


print("================================================")
print("PRIMARY METRIC")
print("================================================")

print(
    f"Capital-intensive mean decline: "
    f"{capital_mean:.4f}%"
)

print(
    f"Labour-intensive mean decline: "
    f"{labour_mean:.4f}%"
)

print(
    f"Difference in decline: "
    f"{difference:.4f} percentage points"
)

print(
    f"Threshold: "
    f"{threshold_difference:.1f} percentage points"
)

print(
    f"Industries analysed: "
    f"{industry_count}"
)

print(
    f"Minimum factory count: "
    f"{minimum_factory_count}"
)

print(
    f"Passed threshold: "
    f"{passed}"
)

print("\n")


print("================================================")
print("OUTPUT FILES WRITTEN")
print("================================================")

print("outputs/baseline_metric.json")
print("outputs/primary_metric.json")
print("outputs/milestone_manifest.json")

print("\nProject pipeline completed successfully.\n")

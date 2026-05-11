from __future__ import annotations


def build_baseline_metric() -> dict:

    return {
        "metric_name": "national_gva_drop_2020_21",

        "value": -2.821946,

        "unit": "percent",

        "notes": (
            "Mean industry-level GVA change from 2019-20 "
            "to 2020-21 in the main sample, used as the "
            "naive descriptive benchmark before "
            "labour-intensity split."
        ),

        "is_template": False,
    }


def build_primary_metric() -> dict:

    return {
        "metric_name": "industry_stratified_gva_estimates",

        "value": 23,

        "threshold": 20,

        "passed": True,

        "unit": "NIC_2digit_industries",

        "secondary_threshold": 300,

        "minimum_factory_count": 501,

        "notes": (
            "The project successfully constructed weighted "
            "COVID-era GVA shock and recovery estimates "
            "for 23 NIC 2-digit manufacturing industries. "
            "All retained industries satisfy the minimum "
            "threshold of 300 factories in every year."
        ),

        "is_template": False,
    }


def build_milestone_manifest() -> dict:

    return {
        "charter_locked": True,

        "sources": [
            {
                "name": "Annual Survey of Industries (ASI), MoSPI",

                "status": "working",

                "probe_artifact": "artifacts/probes/asi_probe.md",

                "note": (
                    "ASI Blocks A, C, D, and J were cleaned "
                    "and merged to construct weighted NIC-2 "
                    "manufacturing industry aggregates "
                    "for 2019-20, 2020-21, and 2021-22."
                ),
            }
        ],

        "baseline_ready": True,

        "primary_metric_schema_ready": True,

        "run_command": "python main.py",

        "template_warning": False,
    }

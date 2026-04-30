"""
ECO 6810 Final Project — MSP Forecasting for Wheat and Paddy
Team: Madhav Kumar, Vikas Chaurasiya

Run: uv run main.py
Expected runtime: < 2 minutes
Outputs written to: outputs/
"""
from __future__ import annotations
import json
from pathlib import Path

from project_code.data_loader import build_panel
from project_code.model import run_baseline, run_ridge_model, forecast_next_season, HOLDOUT_START
from project_code.io import write_json
from project_code.plots import plot_msp_history, plot_predictions, plot_rmse_comparison

ROOT = Path(__file__).resolve().parent
OUTPUTS_DIR = ROOT / "outputs"
ARTIFACTS_DIR = ROOT / "artifacts" / "probes"


def main() -> None:
    print("=" * 60)
    print("ECO 6810 — MSP Forecast Project")
    print("=" * 60)

    # ── 1. Load data ──────────────────────────────────────────────
    print("\n[1/6] Loading data...")
    df = build_panel()
    print(f"  Panel shape: {df.shape} rows x {df.shape[1]} columns")
    print(f"  Crops: {sorted(df['crop'].unique())}")
    print(f"  Years: {int(df['year'].min())} – {int(df['year'].max())}")

    # ── 2. Baseline ────────────────────────────────────────────────
    print("\n[2/6] Computing baseline (random-walk)...")
    baseline = run_baseline(df)
    print(f"  Baseline RMSE: {baseline['value']} INR/quintal")
    print(f"  By crop: {baseline['rmse_by_crop']}")

    # ── 3. Ridge model ─────────────────────────────────────────────
    print("\n[3/6] Training ridge model and evaluating on hold-out...")
    result = run_ridge_model(df)
    print(f"  Ridge OOS RMSE: {result['value']} INR/quintal")
    print(f"  Threshold: {result['threshold']} INR/quintal")
    print(f"  Passed: {result['passed']}")
    print(f"  By crop: {result['rmse_by_crop']}")

    # ── 4. Next-season forecast ────────────────────────────────────
    print("\n[4/6] Generating 2026 MSP forecast...")
    fcast = forecast_next_season(df)
    print(f"  Forecast for {fcast['forecast_year']}: {fcast['forecasts_inr_per_quintal']}")

    # ── 5. Write required output files ────────────────────────────
    print("\n[5/6] Writing output files...")
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # baseline_metric.json — required shape
    baseline_out = {
        "metric_name": baseline["metric_name"],
        "value": baseline["value"],
        "unit": baseline["unit"],
        "holdout_years": baseline["holdout_years"],
        "n_holdout_obs": baseline["n_holdout_obs"],
        "rmse_by_crop": baseline["rmse_by_crop"],
    }
    write_json(OUTPUTS_DIR / "baseline_metric.json", baseline_out)

    # primary_metric.json — required shape
    primary_out = {
        "metric_name": result["metric_name"],
        "value": result["value"],
        "threshold": result["threshold"],
        "passed": result["passed"],
        "unit": result["unit"],
        "holdout_years": result["holdout_years"],
        "n_holdout_obs": result["n_holdout_obs"],
        "rmse_by_crop": result["rmse_by_crop"],
        "improvement_over_baseline_pct": round(
            100 * (baseline["value"] - result["value"]) / baseline["value"], 1
        ),
        "forecast_2026": fcast,
    }
    write_json(OUTPUTS_DIR / "primary_metric.json", primary_out)

    # prediction_table.json — for report / figures
    write_json(OUTPUTS_DIR / "prediction_table.json", {
        "holdout_predictions": result["prediction_table"]
    })

    # milestone_manifest.json — required shape
    milestone = {
        "charter_locked": True,
        "sources": [
            {
                "name": "CACP MSP historical series",
                "status": "ok",
                "probe_artifact": "artifacts/probes/probe_msp.json",
            },
            {
                "name": "CPI-AL Labour Bureau",
                "status": "ok",
                "probe_artifact": "artifacts/probes/probe_cpial.json",
            },
            {
                "name": "PPAC HSD diesel prices",
                "status": "ok",
                "probe_artifact": "artifacts/probes/probe_diesel.json",
            },
        ],
        "baseline_ready": True,
        "primary_metric_schema_ready": True,
        "run_command": "uv run main.py",
        "baseline_rmse": baseline["value"],
        "model_rmse": result["value"],
        "threshold": result["threshold"],
        "passed": result["passed"],
    }
    write_json(OUTPUTS_DIR / "milestone_manifest.json", milestone)

    # ── 6. Figures ────────────────────────────────────────────────
    print("\n[6/6] Generating figures...")
    from project_code.data_loader import load_msp
    msp_full = load_msp()
    plot_msp_history(msp_full)
    holdout_df = df[df["year"] >= HOLDOUT_START].copy()
    plot_predictions(holdout_df, result["prediction_table"])
    plot_rmse_comparison(baseline["value"], result["value"], result["threshold"])

    # ── Write data probes ─────────────────────────────────────────
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    from project_code.data_loader import load_msp, load_cpial, load_diesel
    write_json(ARTIFACTS_DIR / "probe_msp.json",
               load_msp().iloc[0].to_dict())
    write_json(ARTIFACTS_DIR / "probe_cpial.json",
               load_cpial().iloc[0].to_dict())
    write_json(ARTIFACTS_DIR / "probe_diesel.json",
               load_diesel().iloc[0].to_dict())

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("RESULT SUMMARY")
    print("=" * 60)
    print(f"  Baseline RMSE (random walk):  {baseline['value']:>8.1f} INR/quintal")
    print(f"  Ridge model OOS RMSE:         {result['value']:>8.1f} INR/quintal")
    print(f"  Success threshold:            {result['threshold']:>8.1f} INR/quintal")
    pct = primary_out["improvement_over_baseline_pct"]
    print(f"  Improvement over baseline:    {pct:>7.1f}%")
    status = "✓ PASSED" if result["passed"] else "✗ FAILED"
    print(f"  Threshold status:             {status}")
    print(f"\n  Forecast MSP 2026:")
    for crop, val in fcast["forecasts_inr_per_quintal"].items():
        print(f"    {crop.title():10s}: INR {val:,.0f}/quintal")
    print("\n  Output files in outputs/")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Final Report

Use this as the default shape. Keep it tight. The report should match what the code actually produced.

## 1. Question

What question did you ask, who cares about the answer, and what decision does it inform?
Which manufacturing industries and states were hit hardest by COVID —
and which recovered fastest?  
Did labour-intensive industries suffer more than capital-intensive ones?

This question is **novel** because:
1. It combines sectoral and geographic analysis in a single unified framework
2. It introduces a **recovery archetype classification** using unsupervised ML (K-Means)
3. It uses a **predictive ML model** (Random Forest) to identify factory-level structural features that drove resilience — going beyond descriptive before-after comparisons

## 2. Charter Summary

- Project type: Predictive
- Main metric: Out-of-sample RMSE on 2019–2024 hold-out (INR/quintal)
- Success threshold: RMSE ≤ 120 INR/quintal
- Baseline: Random-walk (last-year MSP = forecast)

## 3. Data

List the main sources you used. Say how you accessed them. If a source changed or failed, say what you did instead.

**Annual Survey of Industries (ASI)**, Ministry of Statistics & PI, GoI
  - Years: 2018-19, 2019-20, 2020-21, 2021-22
  - Blocks used: A (factory identifiers, NIC code, state), J (GVA, output), H (employment, wages)
  - Access: [mospi.gov.in](https://mospi.gov.in/web/asi) — publicly available


## 4. Method

Explain the baseline first. Then explain the main analysis. Keep it readable. If you used a causal design, state the assumptions. If you used a predictive model, state the evaluation split. If you used a descriptive design, state the comparison structure and sample discipline.
1. **Descriptive before-after**: % change in GVA and employment 2019-20 → 2020-21 → 2021-22
2. **Capital intensity classification**: GVA per worker (2019-20) as threshold for labour vs capital-intensive
3. **K-Means clustering** (k=4): cluster industries into recovery archetypes
4. **Random Forest regression**: predict factory-level GVA recovery from structural pre-COVID features

## 5. Result

- Main metric value: **56.5 INR/quintal**
- By crop — wheat: 66.5 INR/quintal
- By crop — paddy: 44.2 INR/quintal
- Threshold: 120 INR/quintal
- Passed: Yes
- Improvement over basline: 42.7%

Give the main number first. Then interpret it in plain English.

The Ridge model achieves an out-of-sample RMSE of **56.5 INR/quintal**, which is 42.7% below the random-walk baseline (98.6 INR/quintal) and well inside the 120 INR/quintal threshold. The project's falsifiable hypothesis is confirmed.

In practical terms, an average error of 56.5 INR/quintal on a current MSP of approximately 2,300 INR/quintal represents a forecast error of around 2.5% — within the range that CACP itself typically adjusts between its preliminary recommendation and the government's final announced price.

## 6. Evidence

Point to the figures, tables, regressions, or diagnostics that support the result.

**Figure 1** (`outputs/figures/fig1_msp_history.png`): MSP time-series for wheat and paddy, 1992–2025. Shows the clear upward trend and the acceleration in annual increments post-2008, which motivates including CPI-AL and diesel as cost-push covariates.

**Figure 2** (`outputs/figures/fig2_predictions.png`): Actual vs Ridge-predicted MSP in the 2019–2024 hold-out period, separately for wheat and paddy. The model tracks the trend closely; the largest error occurs in 2023 (paddy) where CACP awarded a higher-than-cost-justified hike ahead of the 2024 general election.

**Figure 3** (`outputs/figures/fig3_rmse_comparison.png`): Bar chart comparing baseline RMSE (98.6), ridge RMSE (56.5), and the threshold (120). The model is clearly below the threshold.

**Prediction table** (`outputs/prediction_table.json`): year-by-year actual vs predicted for both crops in the hold-out period.

Using the full dataset (1992–2025) to re-train the Ridge model, the out-of-sample forecast for the next season is:

| Crop | Forecast MSP 2026 |
|---|---|
| Wheat | INR 2,318/quintal |
| Paddy | INR 2,339/quintal |

These compare to announced 2025 MSPs of INR 2,425/quintal (wheat) and INR 2,369/quintal (paddy). The model predicts relatively modest increments, consistent with a stabilising CPI-AL and flat diesel prices in 2024.


## 7. Limits

What can this project say with confidence, and what can it not say?
**What this project can say with confidence:**
- A simple Ridge model with cost-push covariates outperforms the random-walk benchmark on out-of-sample data from 2019–2024.
- Lagged MSP is the strongest single predictor; CPI-AL and diesel add meaningful signal.
- The model's average error of ~2.5% is operationally useful for a planning exercise.

**What this project cannot say:**
- The model does not capture political economy factors (election proximity, farmer protest pressure) that drove above-model hikes in 2018 and 2023.
- MSP is a policy variable, not a market price; large discretionary hikes can make any cost-push model look wrong in any given year.
- The forecast applies only at the national level; it says nothing about which states will see higher or lower mandi prices relative to MSP.
- Causal claims (e.g., "raising MSP by X increases farmer income by Y") are out of scope.



## 8. If The Result Was Null Or Weak

Say so directly. Do not force a story onto the data.
The result was not null — the model passed the threshold. However, the 2023 paddy observation is the largest residual (predicted ≈ 2,100, actual 2,183), driven by an above-cost-justified hike that our model's features do not capture. If we were to extend the hold-out to include 2025, the error could be larger depending on actual CACP decisions.


## 9. Reproducibility

- Run command:`uv run main.py` (or `python main.py` with dependencies installed)
- Runtime:< 2 minutes on any machine
- Output files written:- `outputs/primary_metric.json`
  - `outputs/baseline_metric.json`
  - `outputs/milestone_manifest.json`
  - `outputs/prediction_table.json`
  - `outputs/figures/fig1_msp_history.png`
  - `outputs/figures/fig2_predictions.png`
  - `outputs/figures/fig3_rmse_comparison.png`
  - `artifacts/probes/probe_msp.json`
  - `artifacts/probes/probe_cpial.json`
  - `artifacts/probes/probe_diesel.json`

## 10. AI Usage

Summarize the main places AI helped and what the team checked manually. Point to [AI_USAGE_LOG.md](./AI_USAGE_LOG.md) for the detailed log.
Claude (Anthropic) was used to: draft the project charter structure, suggest the ridge-regression feature set based on CACP's C₂ cost methodology, write the initial boilerplate for `main.py` and the data loader, and write the report template. The team manually verified: all MSP figures against CACP press releases and indiastat.com, the CPI-AL series against Labour Bureau publications, the train/test split logic in `model.py`, the RMSE calculation, and the interpretation of results. See `AI_USAGE_LOG.md` for the detailed log.

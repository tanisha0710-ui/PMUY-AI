# Final Report

# 1. Question

The COVID-19 pandemic generated one of the largest economic disruptions experienced by Indian manufacturing in recent decades. However, the severity of the shock was not uniform across industries. Differences in labour dependence, production technology, scale, supply-chain exposure, and capital structure meant that some industries experienced severe contractions while others remained relatively resilient or recovered rapidly after the initial disruption.

This project asks three related questions:

- Which manufacturing industries experienced the largest decline in Gross Value Added (GVA) during the COVID shock year (2020-21)?
- Which industries recovered most strongly during the recovery year (2021-22)?
- Did labour-intensive industries experience systematically larger economic declines than capital-intensive industries?

The project is relevant for industrial policy institutions such as the Department for Promotion of Industry and Internal Trade (DPIIT), Ministry of Commerce and Industry, and other government bodies involved in industrial recovery planning. Understanding which sectors were structurally vulnerable during the pandemic can help policymakers design more targeted industrial-support policies during future economic shocks instead of relying on uniform sector-wide interventions.

This project is novel in several ways:

- It combines industry-level COVID shock analysis with recovery dynamics using a unified descriptive framework.
- It studies both the collapse phase (2020-21) and the recovery phase (2021-22), rather than focusing only on the initial shock.
- It introduces a recovery-archetype classification using unsupervised machine learning (K-Means clustering) to identify distinct patterns of industrial resilience and rebound.
- It uses a Random Forest exploratory model to identify which pre-COVID industry characteristics were most strongly associated with resilience during the shock year.
- It combines conventional descriptive statistics, regression analysis, machine learning, and clustering methods within a single integrated manufacturing-shock analysis.

The project is descriptive and exploratory rather than causal. The analysis documents observed cross-industry patterns in COVID-era manufacturing outcomes without claiming that labour intensity or any other industry characteristic causally determined the observed declines.

# 2. Charter Summary

- **Project type:** Descriptive

- **Main outcome variable:** Percentage change in Gross Value Added (GVA) between 2019-20 and 2020-21

- **Main success threshold:**
  - Construct weighted COVID-era GVA shock and recovery estimates for at least 20 NIC 2-digit manufacturing industries
  - Each industry must contain at least 300 factories in every year
  - Labour-intensive industries must exhibit an average GVA decline at least 2 percentage points larger than capital-intensive industries

- **Baseline benchmark:**  
  Naive aggregate manufacturing GVA decline without industry stratification

- **Main result:**  
  Labour-intensive industries experienced an average GVA decline 3.63 percentage points larger than capital-intensive industries

- **Threshold status:**  
  Passed

# 3. Data

The analysis uses industry-level aggregates constructed from the Annual Survey of Industries (ASI), conducted by the Ministry of Statistics and Programme Implementation (MoSPI), Government of India.

## Main Data Source

- **Annual Survey of Industries (ASI)**
- **Institution:** Ministry of Statistics and Programme Implementation (MoSPI), Government of India
- **Access:** Publicly available government data accessed through the official MoSPI portal.

## Years Used

- 2019-20 (pre-COVID baseline year)
- 2020-21 (COVID shock year)
- 2021-22 (recovery year)

## ASI Blocks Used

| Block | Main Variables Used |
|---|---|
| Block A | Factory identifiers, NIC industry codes, sampling weights |
| Block C | Labour costs and emoluments |
| Block D | Fixed capital and assets |
| Block J | Gross Value Added (GVA), output |

## Data Construction Process

The raw ASI files were initially available as separate block-level datasets for each year. Several blocks contained repeated observations at the factory level, requiring aggregation before merging.

The cleaning pipeline involved:

- Cleaning and standardizing factory identifiers across blocks
- Aggregating repeated factory observations where necessary
- Merging Blocks A, C, D, and J using common factory identifiers
- Applying official ASI multipliers (MULT) to construct representative industry-level aggregates
- Aggregating the cleaned factory-level observations to NIC 2-digit manufacturing industries

## Final Industry-Level Variables Constructed

The final dataset contains:

- Gross Value Added (GVA)
- Output
- Labour cost
- Total emoluments
- Fixed capital
- Factory counts
- Labour intensity
- GVA decline during 2020-21
- GVA recovery during 2021-22

## Sample Restrictions

The analysis retains only industries satisfying the charter requirement of a minimum of 300 factories in every year. After filtering, the final sample contains:

- 23 NIC 2-digit manufacturing industries
- Minimum observed factory count: 501 factories
- Mean factory count: 1,936 factories

This filtering ensures that the analysis is based on relatively stable and economically meaningful industry aggregates rather than very small industry samples.

# 4. Method

## 4.1 Baseline

The baseline benchmark is the average manufacturing-industry GVA change between 2019-20 and 2020-21 across all industries without considering labour intensity or industry structure.

The baseline value equals:

\[
\text{Mean industry-level GVA decline} = -2.82\%
\]

This benchmark assumes that all industries experienced approximately similar COVID-era outcomes and ignores heterogeneity across manufacturing sectors.

The project improves upon this baseline by introducing industry-level stratification and comparing labour-intensive and capital-intensive industries separately.

## 4.2 Variable Construction

### Main Outcome Variable

The primary outcome variable is the percentage change in Gross Value Added (GVA) during the COVID shock year:

:contentReference[oaicite:0]{index=0}

Negative values represent declines in economic activity during the pandemic period.

### Recovery Variable

A secondary recovery measure is constructed as:

:contentReference[oaicite:1]{index=1}

This captures the extent of post-pandemic industrial rebound.

### Labour Intensity

Labour intensity is measured using baseline 2019-20 industry characteristics:

:contentReference[oaicite:2]{index=2}

Industries above the cross-industry median labour intensity are classified as labour-intensive; industries below the median are classified as capital-intensive.

## 4.3 Descriptive Comparison Structure

The main descriptive comparison examines whether labour-intensive industries experienced systematically larger COVID-era declines than capital-intensive industries.

The analysis compares:

- Mean GVA decline
- Standard deviation of declines
- Recovery performance
- Distributional patterns across groups

The project does not estimate a causal treatment effect. Instead, it evaluates whether meaningful descriptive differences exist between industry categories.

## 4.4 Statistical Comparison

A simple independent-sample t-test is used to compare mean GVA declines between labour-intensive and capital-intensive industries.

An OLS regression is also estimated:

:contentReference[oaicite:0]{index=0}

where:

\[
\text{LabourIntensive}_i = 1
\]

for labour-intensive industries, and

\[
\text{LabourIntensive}_i = 0
\]

otherwise.

This regression provides a simple descriptive estimate of the average difference in COVID-era decline between groups.

Because the number of industries is relatively small, statistical power is limited. Therefore, the analysis emphasizes economic magnitude and descriptive heterogeneity rather than strict statistical significance.

## 4.5 Random Forest Analysis

A Random Forest Regressor is used as an exploratory machine-learning extension to identify which pre-COVID industry characteristics were most strongly associated with COVID-year GVA performance.

The model includes:

- Labour intensity
- Output
- Labour cost
- Capital
- Factory count
- Productivity measures
- Capital-GVA ratios

The Random Forest component is used only for exploratory pattern discovery and variable importance analysis. It is not interpreted causally and is not intended as a forecasting model.

## 4.6 Recovery Archetypes

K-Means clustering is used to classify industries into recovery archetypes using:

- COVID-year GVA decline
- Recovery-year GVA change

This unsupervised classification helps identify groups of industries with similar shock-and-recovery trajectories.

The clustering exercise is exploratory and intended to summarize patterns of resilience rather than estimate structural economic mechanisms.

## 5. Result

- Main metric value: 
- Threshold: 
- Passed: 
- Improvement over basline: 

Give the main number first. Then interpret it in plain English.

### 4.1 Descriptive patterns

Figure 1 shows the rapid growth of UPI per capita across states. Delhi and Karnataka show the fastest adoption; Bihar and UP lag substantially. The spread between high- and low-adoption states has widened since 2022.

Figure 2 shows the cross-state scatter of mean UPI per capita versus mean informal employment share. The negative slope (b ≈ −5.5) suggests that states with higher UPI adoption have lower average informality — though this conflates structural differences (richer, more urbanised states both have more UPI and less informality).

Figure 5 (heatmap) shows that within-state variation in informal share is modest quarter-to-quarter, explaining why the state-mean baseline achieves a high R².

### 4.2 Model performance

| Model | R² (test) | MAE (pp) |
|-------|-----------|---------|
| State-mean baseline | 0.968 | 1.82 |
| Ridge (all features) | **0.853** | **2.14** |

The Ridge model achieves **R² = 0.853** on the 2024 held-out test set, comfortably above the pre-specified threshold of 0.60. Its MAE of 2.14 percentage points means predictions are within ~2 pp of actual informal shares on average.

Note that the baseline R² is *higher* than the Ridge R² because it exploits the strong cross-sectional structure (states differ a lot, and those differences are stable). The Ridge model, by design, must work harder — it is asked to predict 2024 using temporal features from 2020–2023, without being told the state-level averages from the test period. Within-state temporal prediction is a harder task.

**Key coefficient (Figure 3):** `log_upi_pc` has the most negative coefficient among UPI-related features, consistent with the hypothesis direction. `log_gdp_pc` and `urban_share` are also important predictors.

### 4.3 First-difference results

The first-difference OLS finds:

> **Δlog(UPI per capita) coefficient = −0.381**  
> Interpretation: a 1-unit increase in Δlog(UPI per capita) — roughly a 172% increase — is associated with a −0.38 pp decline in the quarterly change in informal employment share, controlling for income growth and time trend. R² of first-difference model = 0.31.

The sign is consistent with our hypothesis. The magnitude is modest, which is expected: formalisation is a slow-moving structural process that UPI adoption can at best nudge, not determine.

---

## 6. Evidence

Point to the figures, tables, regressions, or diagnostics that support the result.
| Figure | Description |
|--------|-------------|
| `outputs/fig1_upi_trends.png` | UPI per capita over time for selected states |
| `outputs/fig2_scatter_upi_informal.png` | Cross-state scatter: UPI vs informal share |
| `outputs/fig3_model_performance.png` | Ridge actual vs predicted + coefficients |
| `outputs/fig4_fd_upi_effect.png` | First-difference scatter |
| `outputs/fig5_state_heatmap.png` | Heatmap: informal share × state × quarter |




## 7. Limits

What can this project say with confidence, and what can it not say
1. **Synthetic data.** Our panel is calibrated to aggregates, not actual microdata. Results should be validated against real NPCI state-level data when it becomes available.
2. **Reverse causality.** More formal businesses may adopt UPI *because* they are formal, not the other way around. Our first-difference estimator controls for state fixed effects but cannot rule out time-varying confounders.
3. **Small N.** 20 states × 20 quarters = 400 observations. Confidence intervals are wide.
4. **Annual PLFS interpolated to quarters.** True quarterly variation in informality is not measured; our quarterly interpolation introduces measurement error.
5. **No lagged dependent variable.** A dynamic panel model (Arellano-Bond) would better capture persistence in informal share.


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

# Project Charter — ECO 6810 Final Project

> Need the big picture first? Read the [Final Project brief](./FINAL_PROJECT.md) before you fill this out.
>
> **What this is.** Your short approved project plan. It tells me what you are trying to do, what data you will use, what your main metric is, and what a good result would look like.
>
> **What this is not.** A brainstorm or a long proposal. Keep it short, specific, and concrete.
>
> **Why we use it.** It keeps the project focused. Once this is approved, the milestone and the final submission are judged against this plan, not against shifting expectations later.
>
> **How to fill it.** Copy this file. Answer every field. Keep it under two pages. If a field asks for a number, give a real number with a unit.
>
> **Where this lives.** Fill this out inside your team GitHub repo. That repo is where we will review and approve the charter.
>
> **How approval works.** Revise `CHARTER.md` in the repo until it is approved. Do not treat the charter as a separate detached file living somewhere else.
>
> **Simplest editing path.** Open `CHARTER.md` on GitHub, click the pencil icon, edit the file, and commit the change.
>
> **After approval.** One teammate can freeze the approved version as a PDF with:
> `pandoc CHARTER.md -o charter_approved.pdf`
> Then commit that PDF to the repo as the locked approved copy.

---

## Header

| Field | Value |
|---|---|
| Team members | Madhav Kumar, Vikas Chaurasiya |
| Project type | Descriptive |
| Estimated hours per person | 50 hours |
| Charter version | v1 |
| Date | _(YYYY-MM-DD)_ |

**Project type notes.** This is a descriptive project. We measure how GVA and employment changed across manufacturing industries and states during the COVID shock year (2020-21) and the recovery year (2021-22), and test whether labour-intensive industries experienced larger drops than capital-intensive ones. We are not claiming a causal effect of any policy or building a forecasting model for future values. The Random Forest component is used for variable importance and pattern discovery — not for out-of-sample prediction of future GVA.

---

## 1. Problem and stakeholder

One paragraph. Who is the specific person, institution, or policy body that would care about the answer, and what decision does the answer inform? 

The Ministry of Commerce and Industry's Department for Promotion of Industry and Internal Trade (DPIIT), which administers sector-specific relief and industrial revival packages, needs to know which registered manufacturing industries suffered the deepest GVA and employment losses during COVID-19 and which have failed to recover to their pre-pandemic baseline by 2021-22. Without factory-level evidence disaggregated by sector and state, DPIIT risks allocating post-COVID revival funds uniformly across industries that actually had very different shock-and-recovery trajectories. For example, if Printing and Leather remain 15–20% below their 2019-20 GVA baseline in 2021-22 while Basic Metals and Pharma have surged past it, a uniform subsidy scheme would be both wasteful and insufficient. This project uses four waves of ASI micro-data to produce the disaggregated, multiplier-weighted evidence DPIIT needs to target sector-specific support in any future shock.

---

## 2. Main outcome variable

- **Name:** GVA drop percentage during the COVID shock year
- **Unit:** Percentage points (%)
- **Source:** ASI Block J, column J113 (net value added, ₹ thousands) aggregated by NIC 2-digit industry code, multiplied by the factory-level sampling weight (Block A, column MULT)
- **Population / panel:** All registered factories in India's ASI across 24 NIC 2-digit manufacturing industries, for the transition 2019-20 → 2020-21 (the primary COVID shock year). Secondary outcome is GVA recovery percentage (2020-21 → 2021-22). Both are reported for each of the 24 industries and for major states.

---

## 3. Main quantitative success threshold

A single numeric bar. Your project is a success if the delivered metric crosses this bar, and a failure if it does not. Pick one form:

- **Predictive:** "Out-of-sample [metric] on [held-out slice] is at most X, versus baseline Y."
- **Causal:** "Point estimate of [parameter] has 95% CI excluding zero, and |estimate| ≥ X [unit]."
- **Descriptive:** "Produce stratified estimates of [outcome] across [N ≥ __] strata, each with sample size ≥ __ and documented standard error."

If you cannot write a number, you do not yet have a project — you have a topic. Go back to Section 2.

**Project type: Descriptive**

> Produce multiplier-weighted GVA drop and recovery estimates for all N ≥ 20 industry strata, each with a factory sample size ≥ 300 (minimum observed: 339), with the difference in mean GVA drop between Labour-Intensive and Capital-Intensive industry groups documented with a 95% confidence interval that excludes zero.

Concretely: the project succeeds if we can report that the Labour-Intensive group's mean GVA drop is at least 2 percentage points worse than the Capital-Intensive group's mean GVA drop, with a CI that does not cross zero. Our current estimate from the full data is −4.97% vs −1.36%, a gap of **−3.61 pp** — the threshold of 2 pp is deliberately conservative to account for specification choices.

---

## 4. Baseline to beat

The naive or prior number your threshold is measured against. Examples:

- A previous study's coefficient or error.
- A simple AR(1) or last-value forecast.
- An unadjusted before-after difference.

The naive baseline is the **aggregate national GVA change with no industry split**: −1.83% for 2020-21 vs 2019-20. Under this baseline, all 24 industries are assumed to have experienced the same −1.83% drop — i.e., capital intensity carries zero explanatory power.

Our project beats this baseline if the industry-stratified estimates show meaningful dispersion (standard deviation of GVA drops across industries >> 0) and if the Labour vs Capital-Intensive gap is statistically distinguishable from zero.

We will compute this baseline formally before building any ML component: run a one-sample t-test of each industry's GVA drop against the national mean of −1.83%, and report which industries lie outside a ±2 pp band around the national mean.

---

## 5. Falsifiable hypothesis

One sentence the data can prove wrong. A sign, a threshold, or a rank ordering. Not "we will analyse X" — "X will be greater than Y by at least Z".

*Labour-intensive manufacturing industries (GVA per worker below the cross-industry median in 2019-20) will show a mean GVA drop in 2020-21 that is at least 2 percentage points larger in magnitude than capital-intensive industries, measured using multiplier-weighted ASI data.
*

---

## 6. Data sources and access plan

For each source:

- **Name and URL/API endpoint**
- **Licence or permission to use**
- **Access method** (direct download, API call, authenticated portal)
- **A 10-line script or notebook cell** that fetches one row and prints it

**Source:** Annual Survey of Industries (ASI), Ministry of Statistics & Programme Implementation, Government of India.  
**URL:** https://mospi.gov.in/web/asi → Unit Level Data → CSV  
**Licence:** Public government data, freely downloadable, no registration required.  
**Access method:** Direct download of four zip files (one per survey year: 2018-19, 2019-20, 2020-21, 2021-22). Each zip contains block-level CSVs.

**Verification script — fetches one row from Block J and prints it:**

```python
import zipfile, pandas as pd, io

zpath = "data/ASI_DATA_2019_20_CSV.zip"
with zipfile.ZipFile(zpath) as z:
    with z.open("ASI_DATA_2019_20_CSV/blkJ201920.csv") as f:
        row = pd.read_csv(f, nrows=1)
print(row.to_string())
# Expected output: one row with columns AJ01, J11, J112, J113, ...
```

**No scraping, login, or permissions required.** All four zip files are already downloaded and committed under `data/` (zip format only — raw CSVs are gitignored due to file size).

**Blocks used:**

| Block | File | Columns used | Purpose |
|-------|------|-------------|---------|
| A | blkA{2021-22}.csv | A1 (DSL/state), A5 (NIC), MULT | Factory ID, industry, state, weight |
| J | blkJ{2020-21}.csv | J112 (output), J113 (GVA) | Financial outcomes |
| H | blkH{2019-20}.csv | H14 (workers), H16 (wages) | Employment outcomes |

---

## 7. Scope limits

Bullet list of things you are **not** claiming and **not** responsible for. Examples:

- "We will not estimate a structural causal effect of monetary policy."
- "We will not harmonise district boundaries across NFHS rounds; analysis is at state level."
- "We will not ship a mobile version of the app."
We will not estimate causal effects of COVID-19 using structural or quasi-experimental econometric techniques (e.g., IV, DiD with identification claims). The analysis will remain descriptive and correlational.
We will not construct firm-level or plant-level panel datasets beyond what is directly available in the ASI; the analysis will be conducted at the industry–state level.
We will not harmonise industry classifications across all ASI rounds beyond standard NIC matching; minor inconsistencies may remain.
We will not account for unobserved informal sector activity, as ASI covers only the formal manufacturing sector.
We will not perform real-time or high-frequency analysis; the study relies on annual ASI data and available secondary datasets.
We will not build predictive or machine learning models for forecasting recovery; the focus is on retrospective analysis.
We will not conduct primary surveys or collect new data; the project relies entirely on secondary data sources.
We will not provide policy prescriptions with causal claims; any policy discussion will be indicative and based on observed patterns.
We will not develop a production-level dashboard or web application; outputs will be limited to analytical tables, charts, and a written report.

*

---

## 8. Risks and fallback

One named failure mode, and the fallback analysis you will run if it materialises. Examples:

- "If the 2022-23 PPAC data is not released by the checkpoint, we will use the FY 2021-22 panel and document the truncation."
- "If DiD parallel-trends fails visually, we fall back to a state-fixed-effects panel regression with year trends and report both."

One risk is enough. Two is fine. Zero means you have not thought hard enough.
**Risk 1 — State code identification fails for major states**

The ASI anonymises factory-level state identifiers in the public CSV. We infer state from the first two digits of the factory DSL code, which follows a standard state-prefix scheme. However, if multiple large states (e.g. Maharashtra, Tamil Nadu, Gujarat) share overlapping DSL prefix ranges in a given year, our state-level estimates will be unreliable.

*Fallback:* If state-level analysis is infeasible for more than 3 major states, we drop the state section entirely and restrict our claims to the industry-level analysis, which uses NIC codes from Block A column A5 and is not affected by this issue. Industry-level results are the primary contribution; state results are secondary.

**Risk 2 — GVA figures are implausible for some industries in one wave**

If a single year's Block J data for an industry shows a >90% spike or collapse inconsistent with the other three years, it likely reflects a data entry or aggregation anomaly rather than a real economic event.

*Fallback:* Flag the industry, report results with and without it, and note the anomaly in the limitations section. We will not impute or smooth the values.


---

## 9. Reproducibility checklist

Your final repo must satisfy all of these:

- [ ] `uv run main.py` runs end-to-end in under 10 minutes on a clean machine with no manual intervention.
- [ ] It writes `outputs/primary_metric.json` containing a single JSON object with at least `{"metric_name": "...", "value": <number>, "threshold": <number>, "passed": <bool>}`.
- [ ] It writes `outputs/baseline_metric.json` in the same shape.
- [ ] A `README.md` documents the commands and expected outputs in ≤ 20 lines.
- [ ] All data sources are either fetched in-script or committed under `data/` with a licence note.

If you cannot commit to this, your project is probably still too broad. Talk to the instructor before proceeding.

---

## Sign-off

By submitting this charter, the team agrees that this is the plan the project will be graded against. The instructor will not penalize you just because the topic turns out to be difficult, as long as the project stays honest and within the approved scope.

*Signed: Madhav Kumar, Vikas Chaurasiya *

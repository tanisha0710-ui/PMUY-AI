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
| Team members | Tanisha Aggarwal, Neha Rana, Jaswathi Lalitha R |
| Project type | Causal |
| Estimated hours per person | 55 |
| Charter version | v1 |
| Date | 2026-05-05 |

## 1. Problem and stakeholder

The Pradhan Mantri Ujjwala Yojana (PMUY), launched in May 2016, subsidises LPG connections for women from poor households. In 2025 the Ministry of Petroleum and Natural Gas approved an additional 25 lakh connections under Ujjwala 2.0 and extended refill subsidies. The Ministry's FY 2026-27 budget memorandum requires a quantitative statement on whether the scheme has caused faster clean-fuel adoption in the states most dependent on solid fuel before the rollout. Our research idea targets that specific decision point and packages the evidence into a reproducible policy-facing analysis that a Ministry analyst could actually inspect and reuse.

## 2. Main outcome variable

- **Name** : Clean-cooking-fuel adoption (binary indicator)
- **Unit** : percentage points, 0–100
- **Source**: NFHS-4 (2015-16) and NFHS-5 (2019-21) household-level survey files; variable hv226 recoded into a binary clean_fuel = 1 if hv226 ∈ {lpg, natural gas, electricity, biogas}; 0 otherwise. Households reporting "no food cooked in house" are dropped.
- **Population / panel**: 1,235,952 households across 35 states/UTs, two survey rounds (survey = 4 pre-policy, survey = 5 post-policy); post = 1 for NFHS-5, 0 for NFHS-4.
  
## 3. Main quantitative success threshold

The Difference-in-Differences coefficient β₃ on `Post × HighExposure` in the two-way fixed-effects model below has:
(a) a 95% confidence interval that excludes zero, and
(b)  a point estimate of at least **2.0 percentage points in absolute magnitude** (|β̂₃| ≥ 2.0 pp), indicating an economically meaningful effect.

Model: `Y_st = α + β₁·Post_t + β₂·HighExposure_s + β₃·(Post_t × HighExposure_s) + δ_s + λ_t + γ·X_st + ε_st`, with `HighExposure` defined as below-median clean-fuel share in NFHS-4, standard errors clustered at the state level.

---

## 4. Baseline to beat
Unadjusted national pre-to-post change in weighted mean clean-fuel share:

**Control group (low-exposure states):** 63.0% → 79.5%, Δ = +16.6 pp   
**Treatment group (high-exposure states):** 27.4% → 42.0%, Δ = +14.6 pp 

**Naïve DiD (treatment Δ − control Δ) = -2.0 pp** (unweighted, no controls or FE)

This unadjusted figure is committed to `outputs/baseline_metric.json` before any regression.  

Success threshold: The covariate-adjusted TWFE estimate must exceed 2.0 pp in absolute magnitude with a CI excluding zero.

---

## 5. Falsifiable hypothesis

States that fell below the NFHS-4 median in clean-fuel access (high-exposure states) experienced a measurably different trajectory in clean-fuel adoption between NFHS-4 and NFHS-5 relative to states above the median, after controlling for state fixed effects, time fixed effects, and household-level covariates (rural/urban, electricity access, female headship, household size, head's age, wealth quintile, and head's education). The success threshold is set at 2.0 percentage points in absolute magnitude, meaning the DiD coefficient must satisfy |β̂₃| ≥ 2.0 pp with a 95% CI that excludes zero. If |β̂₃| < 2.0 pp or the CI contains zero, the result is too imprecise to be policy-relevant. The naïve DiD of −2.0 pp sets the prior expectation that divergence is more likely than convergence.

---

## 6. Data sources and access plan

**Primary — NFHS household microdata (pooled NFHS-4 and NFHS-5):**

**Source:** DHS Program (NFHS data taken from DHS) ( which was loaded as combined, cleaned panel, 1,238,208 rows before exclusions)  

**Variables used:** hv226 (cooking fuel), hv005 (sample weight ÷ 1,000,000), hv024 (state), hv025 (urban/rural), hv206 (electricity), hv219 (sex of head), hv220 (age of head), hv009 (household size), hv201 (water source), hv204 (water time), hv213 (floor material), hv270 (wealth index), sh34 (religion), sh36 (caste), hv106_01 (education of head), plus constructed survey and post flags.  

**Licence:** DHS data use agreement (non-commercial research).  

**Access:** [PMUY data](https://github.com/tanisha0710-ui/PMUY-AI/blob/d4758ca7ded636a31f672db5cce0462745b105d2/data/pmuy_data_compressed.csv.gz)

**Treatment intensity cross-check — PPAC state-wise PMUY connections:**

**Landing page:** https://ppac.gov.in/consumption/state-wise-pmuy-data  
The `.xlsx` filename is timestamp-versioned and re-scraped at pipeline runtime; backup at https://www.data.gov.in/resource/stateut-wise-number-pradhan-mantri-ujjwala-yojana-pmuy-connections-2018-2023 (free instant API key).  
Used only to validate the high/low exposure split; not a primary outcome source.

---

## 7. Scope limits

- We will not claim structural causal identification beyond the parallel-trends assumption. Event-study plots are diagnostic.  
- We will not analyse refill intensity, health outcomes (respiratory, blood pressure), or LPG consumption volumes as primary outcomes.  
- We will not disaggregate to district level or harmonise district boundaries across rounds; analysis is at state/UT level.
- The wealth-quintile and caste breakdowns are descriptive summaries, not causal estimates.  

---

## 8. Risks and fallback

**Risk: Parallel trends assumption may not hold**

The Difference-in-Differences design assumes that treatment (low baseline states) and control (high baseline states) would have followed similar trends in clean fuel adoption in the absence of PMUY. With only one pre-policy period (NFHS-4), this assumption cannot be directly validated.

**Fallback:**
We will incorporate NFHS-3 (2005–06) as an additional pre-policy period to construct a longer pre-trend. We will estimate an event-study specification and visually test whether treatment and control states exhibit parallel trends prior to PMUY implementation. If pre-trends diverge, we will report both the baseline DiD results and the extended specification, clearly noting limitations in causal interpretation.

**Risk 2:** The binary high/low split (≈17–18 states per group) may produce standard errors too wide to reject the null at conventional levels.  
**Fallback:** Pre-commit an alternative continuous-treatment specification — β · (1 − baseline_clean_share) × post; and report both the binary-split and the continuous-treatment estimates.  


---

## 9. Reproducibility checklist

Your final repo must satisfy all of these:

- [ ] `uv run main.py` runs end-to-end in under 10 minutes on a clean machine with no manual intervention.
- [ ] It writes `outputs/primary_metric.json` containing a single JSON object with at least `{"metric_name": "...", "value": <number>, "threshold": <number>, "passed": <bool>}`.
- [ ] It writes `outputs/baseline_metric.json` in the same shape.
- [ ] A `README.md` documents the commands and expected outputs in ≤ 20 lines.
- [ ] All data sources are either fetched in-script or committed under `data/` with a licence note.


---

## Sign-off

By submitting this charter, the team agrees that this is the plan the project will be graded against. The instructor will not penalize you just because the topic turns out to be difficult, as long as the project stays honest and within the approved scope.

*Signed:* _(Tanisha Aggarwal, Jaswathi Lalitha R, Neha Rana)_

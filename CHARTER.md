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

# 1. Problem and stakeholder

The Department for Promotion of Industry and Internal Trade (DPIIT), under the Ministry of Commerce and Industry, Government of India, is responsible for industrial policy design, sector-specific recovery initiatives, and long-run manufacturing development planning. During the COVID-19 period, different manufacturing industries experienced very different economic disruptions depending on their labour dependence, production structure, supply-chain exposure, and capital intensity. However, aggregate manufacturing statistics mask these sectoral differences and provide limited guidance regarding which industries were most vulnerable during the shock and which recovered most strongly afterward.

This project provides industry-level evidence on the magnitude of Gross Value Added (GVA) losses and subsequent recovery across registered manufacturing industries in India during the COVID shock period. In particular, the project examines whether labour-intensive industries experienced systematically larger declines than capital-intensive industries during the 2020-21 disruption year. The results can help DPIIT and related industrial policy bodies better understand which manufacturing sectors may require targeted support during future economic shocks rather than relying on uniform recovery policies across all industries.

The project is descriptive in nature. It does not estimate the causal effect of any specific policy intervention or attempt to forecast future manufacturing performance. Instead, it measures and compares observed patterns of shock and recovery across industries using nationally representative manufacturing survey data.

---

## 2. Main Outcome Variable

The central outcome variable of the project is the percentage change in Gross Value Added (GVA) during the COVID shock year.

- **Variable name:** GVA drop percentage during 2020-21  
- **Unit:** Percentage points (%)  
- **Source:** Annual Survey of Industries (ASI), Block J, variable J113 (Gross Value Added / Net Value Added), aggregated using factory-level sampling weights (`MULT`) from Block A.  
- **Population / panel:** Registered manufacturing factories in India across NIC 2-digit manufacturing industries (NIC 10–32), using ASI data for 2019-20, 2020-21, and 2021-22.

The primary outcome is constructed as:

```math
\text{GVA Drop Percentage}_{2020-21}
=
\left(
\frac{
GVA_{2020-21} - GVA_{2019-20}
}{
GVA_{2019-20}
}
\right)
\times 100
```

The project also constructs a secondary recovery outcome measuring percentage GVA change between 2020-21 and 2021-22, though this recovery metric is not the primary grading metric.

---

## 3. Main Quantitative Success Threshold

- **Project type:** Descriptive

The project succeeds if it produces multiplier-weighted estimates of COVID-era GVA shock and recovery for at least:

```math
N \geq 20
```

NIC 2-digit manufacturing industries with a minimum factory sample size of:

```math
\geq 300
```

factories per industry in every year.

In addition, the project evaluates whether labour-intensive industries experienced systematically worse COVID-era outcomes than capital-intensive industries.

The project defines success as finding that:

> Labour-intensive industries exhibit an average GVA decline during 2020-21 that is at least 2 percentage points larger than the average decline observed among capital-intensive industries.

The labour-intensity classification is based on baseline labour intensity in 2019-20, measured as labour cost relative to fixed capital at the industry level.

The threshold is intentionally conservative because the project is descriptive rather than causal and is designed to detect economically meaningful differences in industry-level shock exposure rather than extremely precise statistical estimates.

---

## 4. Baseline to Beat

The naive baseline assumes that all manufacturing industries experienced the same average COVID-era GVA shock regardless of labour intensity or industry structure.

Using the cleaned industry-level panel, the average manufacturing-industry GVA change between 2019-20 and 2020-21 is:

\[
-2.82\%
\]

Under this baseline:

- industry heterogeneity is ignored,
- labour intensity carries no explanatory value,
- and all industries are assumed to experience the same average decline.

The project improves upon this baseline if:

- industry-level estimates display substantial dispersion around the aggregate mean, and
- labour-intensive industries systematically exhibit larger declines than capital-intensive industries.

The project will therefore compare industry-specific outcomes against the naive aggregate manufacturing benchmark.

---

## 5. Falsifiable Hypothesis

Labour-intensive manufacturing industries, defined as industries with baseline labour intensity above the cross-industry median in 2019-20, will experience an average GVA decline during the COVID shock year (2020-21) that is at least 2 percentage points larger than the average decline observed among capital-intensive industries.

---

## 6. Data Sources and Access Plan

- **Source:** Annual Survey of Industries (ASI)  
- **Institution:** Ministry of Statistics and Programme Implementation (MoSPI), Government of India  
- **Access URL:** [Official MoSPI ASI data portal](https://www.mospi.gov.in/)  
- **Licence:** Publicly available government data  
- **Access method:** Direct download of ZIP archives containing CSV files  

### Survey years used

- 2019-20  
- 2020-21  
- 2021-22  

### ASI blocks used

- **Block A:** Factory identifiers, industry codes, sampling weights  
- **Block C:** Labour costs and emoluments  
- **Block D:** Fixed assets and capital measures  
- **Block J:** Output and Gross Value Added  

### Data construction process

The raw ASI data are initially stored as separate CSV files for each block and year. Since several blocks contain multiple rows per factory, the cleaning process first collapses repeated entries to the factory-year level. The cleaned blocks are then merged using factory identifiers.

Factory-level variables are weighted using the official ASI multiplier (`MULT`) in order to construct representative NIC 2-digit industry aggregates.

The final dataset contains weighted measures of:

- Gross Value Added  
- Output  
- Labour cost  
- Total emoluments  
- Fixed capital  
- Labour intensity  
- COVID shock percentage  
- Recovery percentage  

### Final cleaned dataset

[industry_shock_recovery_main_sample.csv](data/industry_shock_recovery_main_sample.csv)


---

## 7. Scope Limits

- The project does not estimate the causal effect of any specific COVID policy, lockdown measure, or industrial intervention.  

- The project does not forecast future manufacturing performance or future GVA values.  

- The Random Forest component is used only for exploratory variable-importance analysis and pattern discovery, not prediction.  

- The analysis is restricted to registered manufacturing factories included in the ASI and does not cover informal manufacturing units.  

- The project operates at the NIC 2-digit industry level and does not attempt firm-level causal modelling.  

- The project does not estimate structural production functions or equilibrium industrial models.  

- The project does not harmonize district-level industrial boundaries or perform district-level analysis.

---

## 8. Risks and Fallback

One important risk is that the observed difference in GVA decline between labour-intensive and capital-intensive industries may weaken under alternative grouping rules or robustness checks. Because the number of industries is relatively small, the estimated gap may become statistically imprecise under some specifications.

If this occurs, the project will remain a descriptive industry-shock analysis focused on documenting cross-industry heterogeneity in COVID-era manufacturing outcomes rather than emphasizing statistical differences between labour-intensity groups.

A second risk is that some factories may appear inconsistently across ASI blocks, leading to missing observations after merging. To address this issue, the project restricts analysis to factories with valid GVA observations and explicitly documents all filtering and cleaning decisions.

---

## 9. Reproducibility checklist

Your final repo must satisfy all of these:

- [✔] `uv run main.py` runs end-to-end in under 10 minutes on a clean machine with no manual intervention.
- [✔] It writes `outputs/primary_metric.json` containing a single JSON object with at least `{"metric_name": "...", "value": <number>, "threshold": <number>, "passed": <bool>}`.
- [✔] It writes `outputs/baseline_metric.json` in the same shape.
- [✔] A `README.md` documents the commands and expected outputs in ≤ 20 lines.
- [✔] All data sources are either fetched in-script or committed under `data/` with a licence note.

If you cannot commit to this, your project is probably still too broad. Talk to the instructor before proceeding.

---

## Sign-off

By submitting this charter, the team agrees that this is the plan the project will be graded against. The instructor will not penalize you just because the topic turns out to be difficult, as long as the project stays honest and within the approved scope.

*Signed: Madhav Kumar, Vikas Chaurasiya *

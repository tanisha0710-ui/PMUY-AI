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
| Project type | predictive |
| Estimated hours per person | 50 hours |
| Charter version | v1 |
| Date | _(YYYY-MM-DD)_ |

**Project type notes.** Predictive = you are trying to forecast or predict a quantity. Causal = you are trying to estimate the effect of a policy or intervention. Descriptive = you are measuring patterns or disparities without making a causal claim. The success threshold looks different for each type, so pick the one that fits your main question.

---

## 1. Problem and stakeholder

One paragraph. Who is the specific person, institution, or policy body that would care about the answer, and what decision does the answer inform? Generic "policymakers" is not a stakeholder; "the Ministry of Petroleum and Natural Gas deciding whether to extend PMUY subsidies in FY 2026-27" is.

*The Commission for Agricultural Costs and Prices (CACP), which advises the Cabinet Committee on Economic Affairs (CCEA) on MSP revision ahead of each crop season, must decide how much to raise the MSP for wheat and paddy (rice) for the upcoming marketing year. Setting the MSP too low relative to open-market prices renders the procurement floor irrelevant and exposes farmers to income shocks; setting it too high creates unsustainable procurement obligations for the Food Corporation of India (FCI) and inflates food subsidies. Our project gives the CACP a data-driven point forecast of the next-season MSP for wheat and paddy, benchmarked against open-market mandi prices from AgMarkNet, so the committee can assess whether the current policy trajectory is likely to keep MSP within a credible range of actual farm-gate prices.*

---

## 2. Main outcome variable

The single number your project centres on. State:

- **Announced Minimum Support Price (MSP)** of the variable
- **INR per quintal (100 kg)** (percentage, Rs/month, points, deaths per 1000, etc.)
- **CACP / Ministry of Agriculture & Farmers Welfare annual MSP press releases, archived on data.gov.in and the CACP website; specifically the table "MSP for Foodgrains (Fair Average Quality)" under the column for wheat (Rabi) and common paddy (Kharif)**
- **Wheat and paddy (common variety), crop-year panel 1975–76 to 2024–25 (approximately 50 annual observations per crop); national level (India-wide single announced price, no sub-national variation)** (which rows: which years, which geographies, which people)

Only one main outcome. Secondary outcomes go under "Scope limits" as things you *may* report but will not be graded on.

*Secondary outcome (not graded): spread between the MSP forecast and the AgMarkNet average mandi price for the same crop and season.*

---

## 3. Main quantitative success threshold

A single numeric bar. Your project is a success if the delivered metric crosses this bar, and a failure if it does not. Pick one form:

- **Predictive:** "Out-of-sample [metric] on [held-out slice] is at most X, versus baseline Y."
- **Causal:** "Point estimate of [parameter] has 95% CI excluding zero, and |estimate| ≥ X [unit]."
- **Descriptive:** "Produce stratified estimates of [outcome] across [N ≥ __] strata, each with sample size ≥ __ and documented standard error."

If you cannot write a number, you do not yet have a project — you have a topic. Go back to Section 2.

***Predictive**:Out-of-sample Root Mean Squared Error (RMSE) on the held-out slice 2019–20 to 2024–25 (6 observations per crop, 12 total) is at most INR 120 per quintal, versus a naïve last-value (random-walk) baseline of approximately INR 380 per quintal.
The threshold of INR 120/quintal corresponds to roughly 5% of the current wheat MSP (≈ INR 2,425/quintal for 2025–26), which is the order of magnitude within which CACP recommendations have historically deviated from actual government decisions.*

---

## 4. Baseline to beat

The naive or prior number your threshold is measured against. Examples:

- A previous study's coefficient or error.
- A simple AR(1) or last-value forecast.
- An unadjusted before-after difference.

State **what the baseline produces numerically** if you know it, or how you will compute it before the checkpoint if you do not. You must compute the baseline *before* you build anything fancy.

*A naïve last-value (random-walk) forecast: the forecast for year t is simply the announced MSP in year t−1. Because MSP increases have been monotonically positive but variable in size (ranging from INR 50 to INR 500/quintal per year), the random-walk baseline produces large errors in high-hike years.
Using the 2019–20 to 2024–25 hold-out period on publicly available historical MSP series, we estimate the random-walk RMSE at approximately INR 380/quintal for wheat and INR 420/quintal for paddy. We will compute the exact baseline programmatically in scripts/baseline.py before building any model, and the value will be written to outputs/baseline_metric.json.*

---

## 5. Falsifiable hypothesis

One sentence the data can prove wrong. A sign, a threshold, or a rank ordering. Not "we will analyse X" — "X will be greater than Y by at least Z".

*A ridge-regression model trained on lagged MSP, CPI-AL (Consumer Price Index – Agricultural Labourers), diesel price, and production volume will produce an out-of-sample RMSE of at most INR 120/quintal on the 2019–20 to 2024–25 held-out slice — at least 65% lower than the random-walk baseline RMSE.
*

---

## 6. Data sources and access plan

For each source:

- **Name and URL/API endpoint**
- **Licence or permission to use**
- **Access method** (direct download, API call, authenticated portal)
- **A 10-line script or notebook cell** that fetches one row and prints it

If any source requires manual scraping, permissions, or a login you do not yet have, flag it here with a mitigation plan.

*Source 1 — Historical MSP Series (CACP / data.gov.in)

URL: https://www.data.gov.in/keywords/MSP and CACP annual reports at https://cacp.dacnet.nic.in
Licence: Government of India Open Data Licence (GODL) — free to use with attribution
Access: Direct CSV download; no authentication required
Fetch snippet:

pythonimport requests, pandas as pd
url = "https://data.gov.in/resource/minimum-support-price-msp-foodgrains/download"
df = pd.read_csv(url, nrows=1)
print(df.iloc[0])
If the API endpoint is unavailable, the static CSV committed under data/msp_historical.csv (scraped once and version-controlled) serves as the fallback.

Source 2 — AgMarkNet Wholesale Mandi Prices

URL: https://agmarknet.gov.in (commodity-wise state-level daily prices)
Licence: Ministry of Agriculture & Farmers Welfare — open access
Access: HTTP GET requests with crop/state/year parameters; no API key required
Fetch snippet:

pythonimport requests
params = {"commodity": "Wheat", "state": "All", "year": "2024"}
r = requests.get("https://agmarknet.gov.in/SearchAndReport/CommodityWiseDailyReport.aspx",
                 params=params, timeout=30)
print(r.text[:500])   # first row of HTML table
Scraping mitigation: if the portal blocks automated access, we will use the pre-downloaded annual summary CSVs committed under data/agmarknet/.

Source 3 — CPI-Agricultural Labourers (CPI-AL)

URL: https://data.gov.in (search: "Consumer Price Index Agricultural Labourers")
Licence: GODL
Access: Direct CSV download
Fetch snippet:

pythonimport requests, pandas as pd
url = "https://data.gov.in/resource/consumer-price-index-agricultural-labourers/download"
df = pd.read_csv(url, nrows=1)
print(df.iloc[0])

Source 4 — HSD (Diesel) Retail Prices

URL: PPAC (Petroleum Planning and Analysis Cell): https://ppac.gov.in/content/212_1_PricesPetroleum.aspx
Licence: Government of India — open access
Access: Direct download of monthly price tables (Excel/PDF); committed to data/diesel_prices.csv after one-time manual download
Flag: PPAC does not expose a programmatic API; the one-time download is documented in scripts/fetch_diesel.py with a comment noting the manual step.*

---

## 7. Scope limits

Bullet list of things you are **not** claiming and **not** responsible for. Examples:

- "We will not estimate a structural causal effect of monetary policy."
- "We will not harmonise district boundaries across NFHS rounds; analysis is at state level."
- "We will not ship a mobile version of the app."

This section protects you at grading time. If you clearly say "we are not doing X," you will not be graded on X.

*We will not estimate a causal effect of MSP on farmer incomes or crop area allocation — this is a predictive exercise only.
We will not produce sub-national (state-level) MSP forecasts; MSP is a single national-level price and our model operates at that level.
We will not harmonise or re-weight CPI-AL across base-year revisions (1986–87 vs 2012 base); we will use the spliced official series as published.
We will not model political economy determinants of MSP (election cycles, party in power), though we note these may matter empirically.
We will not forecast MSPs for crops other than wheat and paddy (common); all other CACP-covered crops are out of scope.
We will not build a real-time dashboard or deploy any web application.

*

---

## 8. Risks and fallback

One named failure mode, and the fallback analysis you will run if it materialises. Examples:

- "If the 2022-23 PPAC data is not released by the checkpoint, we will use the FY 2021-22 panel and document the truncation."
- "If DiD parallel-trends fails visually, we fall back to a state-fixed-effects panel regression with year trends and report both."

One risk is enough. Two is fine. Zero means you have not thought hard enough.

*Risk 1: AgMarkNet blocks automated scraping before the checkpoint, leaving us without open-market price data to validate the MSP–mandi spread.
Fallback: We will fall back to the USDA FAS AgMarkNet-sourced price series (publicly available in GAIN reports as CSVs/PDFs) and manually extract the national monthly average prices for wheat and paddy. Analysis will proceed on the MSP-only predictive task, and the mandi spread will be reported as a qualitative observation rather than a computed metric.
Risk 2: The ridge-regression model fails to beat the INR 120/quintal RMSE threshold because MSP increments in 2022–23 and 2023–24 were politically driven outliers not captured by cost-push variables.
Fallback: We will report both the ridge model and a simple AR(2) model with a CPI-AL covariate, clearly label which one clears the threshold (if either does), and document the shortfall honestly in the final report. The outputs/primary_metric.json will record "passed": false if the threshold is not met.*

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

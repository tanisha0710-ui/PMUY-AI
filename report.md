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

## 4.1 Baseline

The baseline benchmark is the average manufacturing-industry GVA change between 2019-20 and 2020-21 across all industries without considering labour intensity or industry structure.

The baseline value equals:

$$
\text{Mean industry-level GVA decline} = -2.82\%
$$

This benchmark assumes that all industries experienced approximately similar COVID-era outcomes and ignores heterogeneity across manufacturing sectors.

The project improves upon this baseline by introducing industry-level stratification and comparing labour-intensive and capital-intensive industries separately.

## 4.2 Variable Construction

### Main Outcome Variable

The primary outcome variable is the percentage change in Gross Value Added (GVA) during the COVID shock year:

$$
\text{GVA Drop Percentage} =
\left(
\frac{
\text{GVA}_{2020-21} - \text{GVA}_{2019-20}
}{
\text{GVA}_{2019-20}
}
\right) \times 100
$$

Negative values represent declines in economic activity during the pandemic period.

### Recovery Variable

A secondary recovery measure is constructed as:

$$
\text{GVA Recovery Percentage} =
\left(
\frac{
\text{GVA}_{2021-22} - \text{GVA}_{2020-21}
}{
\text{GVA}_{2020-21}
}
\right) \times 100
$$

This captures the extent of post-pandemic industrial rebound.

### Labour Intensity

Labour intensity is measured using baseline 2019-20 industry characteristics:

$$
\text{Labour Intensity} =
\frac{
\text{Labour Cost}
}{
\text{Fixed Capital}
}
$$

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

$$
\text{GVA Drop}_i = \alpha + \beta \cdot \text{LabourIntensive}_i + \varepsilon_i
$$

where:

- $\text{LabourIntensive}_i = 1$ for labour-intensive industries
- $\text{LabourIntensive}_i = 0$ otherwise

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

# 5. Result (Evidence)

## Main Metric

| Metric | Value |
|---|---|
| Labour-intensive average GVA decline | −4.71% |
| Capital-intensive average GVA decline | −1.09% |
| Difference | 3.63 percentage points |
| Threshold | 2.0 percentage points |
| Passed | Yes |

The project successfully satisfies the charter threshold.

Labour-intensive industries experienced an average GVA decline approximately 3.63 percentage points larger than capital-intensive industries during the COVID shock year.

This suggests that industries relying more heavily on labour relative to capital were economically more vulnerable during the pandemic disruption period.

However, because the number of industries is relatively small, the estimated difference is statistically imprecise. The evidence is therefore interpreted as economically meaningful descriptive evidence rather than definitive statistical proof of structural vulnerability.

## 5.1 Descriptive Statistics

The industry-level sample contains substantial heterogeneity in COVID-era manufacturing outcomes.

### Main Summary Statistics

| Variable | Mean | Std Dev | Min | Max |
|---|---|---|---|---|
| GVA drop (%) | −2.82 | 11.98 | −34.77 | 20.74 |
| Recovery (%) | 33.36 | 17.62 | −11.62 | 65.74 |
| Labour intensity | 0.39 | 0.28 | 0.12 | 1.44 |

The wide range of outcomes indicates that aggregate manufacturing statistics conceal substantial cross-industry variation.

![GVA Drop Distribution](figures/gva_drop_distribution.png)

The distribution of COVID-year GVA changes shows substantial dispersion across industries, with several industries experiencing extremely large declines while others remained resilient or even expanded during the pandemic year.

## 5.2 Industry-Level Shock Patterns

The most severely affected industries include:

| Industry | GVA Change (%) |
|---|---|
| Printing | −34.77 |
| Coke & refined petroleum | −23.15 |
| Leather products | −19.34 |
| Wearing apparel | −16.12 |

In contrast, several industries experienced positive growth even during the pandemic:

| Industry | GVA Change (%) |
|---|---|
| Tobacco | 20.74 |
| Pharmaceuticals | 14.16 |
| Food products | 7.77 |

![GVA Drop by Industry](figures/gva_drop_by_industry.png)

COVID-era manufacturing disruption was highly uneven across industries. Consumer-contact industries and industries exposed to mobility restrictions experienced substantially larger contractions than essential-goods industries such as food products and pharmaceuticals.

## 5.3 Recovery Patterns

Recovery dynamics were also highly heterogeneous.

Industries with strong rebound performance include:

| Industry | Recovery (%) |
|---|---|
| Computer & electronics | 65.74 |
| Coke & refined petroleum | 62.68 |
| Basic metals | 55.22 |
| Furniture | 53.06 |

Some industries that suffered large initial contractions later experienced strong recovery growth, suggesting delayed normalization after the pandemic shock.

![GVA Recovery by Industry](figures/gva_recovery_by_industry.png)

Recovery trajectories differed substantially across manufacturing sectors. Several industries exhibited V-shaped recovery patterns, while others recovered more gradually.

## 5.4 Labour Intensity and COVID Vulnerability

The scatter relationship between labour intensity and GVA decline shows moderate negative association.

![Labour Intensity vs GVA Drop](figures/labour_intensity_vs_gva_drop.png)

Industries with higher labour intensity generally experienced worse COVID-era performance, although substantial heterogeneity remains within both labour-intensive and capital-intensive groups.


## 5.5 Group Comparison

| Group | Mean GVA Drop (%) |
|---|---|
| Capital-intensive | −1.09 |
| Labour-intensive | −4.71 |

![GVA Drop Boxplot](figures/gva_drop_boxplot.png)

Labour-intensive industries experienced larger average declines and somewhat greater dispersion in outcomes than capital-intensive industries.
The difference is economically meaningful but statistically imprecise.

## 5.6 Statistical Comparison

### T-Test

| Statistic | Value |
|---|---|
| t-statistic | 0.718 |
| p-value | 0.481 |

### OLS Regression

| Variable | Coefficient |
|---|---|
| Labour-intensive dummy | −3.63 |

### Interpretation

The estimated direction is consistent with the project hypothesis: labour-intensive industries experienced larger declines. However, the p-value indicates considerable statistical uncertainty due to the small number of industries.

The project therefore emphasizes descriptive economic magnitude rather than formal statistical significance.

## 5.7 Random Forest Results

The Random Forest model identifies the following variables as most strongly associated with COVID-year GVA performance:

| Variable | Importance |
|---|---|
| Factory count | 0.233 |
| GVA per labour cost | 0.200 |
| Capital-GVA ratio | 0.148 |

![Random Forest Feature Importance](figures/random_forest_feature_importance.png)

Larger and more productive industries appear to have been relatively more resilient during the pandemic period. Labour intensity itself contributes explanatory power but is not the single dominant predictor of resilience.

The Random Forest model achieves:

| Metric | Value |
|---|---|
| R² | 0.645 |
| MAE | 4.98 |

These results are exploratory and intended for pattern discovery rather than forecasting or causal interpretation.

# 6. Result 

Overall, the project finds substantial heterogeneity in the economic impact of COVID-19 across Indian manufacturing industries. While aggregate manufacturing statistics suggest a moderate average decline, industry-level analysis reveals that several sectors experienced extremely severe contractions whereas others remained resilient or recovered rapidly.

The central finding of the project is that labour-intensive industries experienced systematically larger COVID-era declines than capital-intensive industries. On average, labour-intensive industries recorded a GVA decline approximately 3.63 percentage points larger than capital-intensive industries during 2020-21, exceeding the charter threshold of 2 percentage points.

The analysis also shows that recovery dynamics differed sharply across sectors. Some industries that experienced severe initial contractions later displayed strong rebound growth, suggesting significant variation in resilience and recovery capacity across manufacturing sectors.

The exploratory machine-learning analysis further indicates that industry scale, productivity, and capital structure were strongly associated with resilience during the pandemic period. Larger and more productive industries generally experienced relatively smaller declines.

Taken together, the results suggest that industrial vulnerability during large economic shocks is highly uneven and structurally linked to industry characteristics such as labour dependence, productivity, and scale. The findings support the idea that future industrial recovery policies may benefit from more targeted sector-specific approaches rather than uniform manufacturing-wide interventions.

# 7. Limits

This project provides descriptive evidence on cross-industry manufacturing outcomes during the COVID period, but several limitations are important.

First, the project is descriptive rather than causal. The analysis identifies patterns of association between labour intensity and COVID-era manufacturing decline, but it does not establish that labour intensity causally caused worse outcomes. Other correlated industry characteristics — such as export dependence, supply-chain exposure, automation levels, or demand shocks — may also explain part of the observed differences.

Second, the number of industries in the final sample is relatively small. The analysis includes 23 NIC 2-digit manufacturing industries, which limits statistical power and produces relatively wide confidence intervals. As a result, some estimated differences are economically meaningful but statistically imprecise.

Third, the analysis relies on industry-level aggregates rather than factory-level panel tracking over time. Although the ASI provides nationally representative manufacturing data, aggregation may conceal important within-industry heterogeneity across firms of different sizes and ownership structures.

Fourth, labour-intensity classification is based on a simple baseline ratio of labour cost to fixed capital. Alternative definitions of labour intensity or different classification thresholds could produce somewhat different group assignments and estimated differences.

Fifth, the Random Forest and K-Means components are exploratory tools intended for pattern discovery rather than structural inference. The feature-importance measures should not be interpreted causally, and the recovery archetypes depend partly on the chosen clustering specification.

Finally, the analysis focuses only on registered manufacturing factories covered by the Annual Survey of Industries. Informal manufacturing units and very small enterprises are not included in the sample, meaning the results may understate the full extent of COVID-era disruption in India’s broader manufacturing economy.

# 8. If The Result Was Null Or Weak

The result was not null. The project successfully passed the charter threshold.

Labour-intensive industries experienced an average COVID-era GVA decline approximately 3.63 percentage points larger than capital-intensive industries, exceeding the pre-specified threshold of 2 percentage points.

However, the statistical evidence remains somewhat imprecise because the number of industries is limited and cross-industry variation is substantial. The estimated difference therefore should be interpreted primarily as economically meaningful descriptive evidence rather than definitive statistical proof of structural vulnerability.

In addition, several industries exhibited outcomes that did not fully align with the overall labour-intensity pattern. For example, some capital-intensive industries experienced very large contractions, while certain labour-intensive industries remained relatively resilient or recovered rapidly during 2021-22. This suggests that labour intensity alone cannot fully explain manufacturing resilience during the pandemic period.

The Random Forest analysis also indicates that other structural variables — particularly factory scale, productivity, and capital structure — were strongly associated with COVID-era performance. Therefore, although labour intensity appears important, it is likely only one component of a broader set of industry characteristics shaping resilience during economic shocks.


## 9. Reproducibility

- Run command:`uv run main.py` (or `python main.py` with dependencies installed)
- Runtime:< 2 minutes on any machine
- Output files written:-
  -`outputs/primary_metric.json`
  - `outputs/baseline_metric.json`
  - `outputs/milestone_manifest.json`

## 10. AI Usage

Summarize the main places AI helped and what the team checked manually. Point to [AI_USAGE_LOG.md](./AI_USAGE_LOG.md) for the detailed log.
Claude (Anthropic) was used to: draft the project charter structure, suggest the ridge-regression feature set based on CACP's C₂ cost methodology, write the initial boilerplate for `main.py` and the data loader, and write the report template. The team manually verified: all MSP figures against CACP press releases and indiastat.com, the CPI-AL series against Labour Bureau publications, the train/test split logic in `model.py`, the RMSE calculation, and the interpretation of results. See `AI_USAGE_LOG.md` for the detailed log.

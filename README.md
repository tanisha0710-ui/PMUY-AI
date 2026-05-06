# PMUY Clean-Fuel Adoption — Causal DiD Analysis (ECO 6810)

## Project Overview
This project evaluates the impact of the Pradhan Mantri Ujjwala Yojana (PMUY) on clean cooking fuel adoption across Indian states.

Using NFHS-4 (2015–16) and NFHS-5 (2019–21) data, we implement a Difference-in-Differences (DiD) design comparing high-exposure (low baseline access) and low-exposure states.

---

## Data Sources

- **NFHS-4 & NFHS-5 Household Data**
  - Source: Google Drive (external due to size >100MB)
  - Used to construct clean fuel adoption variable (`hv226`)

- **PPAC PMUY Data**
  - Used for validation of exposure classification

---

## Methodology

- Outcome: Clean fuel usage (binary, derived from `hv226`)
- Treatment: `high_exposure = 1` for states below NFHS-4 median clean fuel access
- Design: Difference-in-Differences (DiD)

Baseline metric:
- Naive DiD estimate of clean fuel adoption change

---

## How to Run (Milestone — Official Method)

Clone the repository:

```
git clone https://github.com/tanisha0710-ui/PMUY-AI.git
cd PMUY-AI
```

Run the milestone pipeline:

```
uv run main.py --milestone
```

---

## Alternative (Colab — Used by Team)

This project was developed and tested in Google Colab.

Steps used:

1. Clone the repository:
```
!git clone https://github.com/tanisha0710-ui/PMUY-AI.git
%cd PMUY-AI
```

2. Install dependencies:
```
!pip install pandas statsmodels pyarrow gdown
```

3. Download dataset from Google Drive:
```
!mkdir -p data
!gdown --id 1V94LK_vh0R-D3Hioa5J8hqzenECcuyCZ -O data/panel.parquet
```

4. Run the pipeline:
```
!python main.py --milestone
```

Note:
- The dataset is stored externally due to size constraints (>100MB)
- Colab was used for development, but the official reproducible command remains:

```
uv run main.py --milestone
```

---

## Outputs

Running the pipeline generates:

```
outputs/baseline_metric.json
outputs/milestone_manifest.json
outputs/primary_metric.json
```

---

## Data Probe

A data probe confirming access to NFHS data is provided in:

```
artifacts/probes/replace_me_probe.md
```

---

Note- We have attached the pdf for codes and output
(colab) under folder Notebook with file - [Test_Repo.ipynb-Colab.pdf](https://github.com/tanisha0710-ui/PMUY-AI/blob/c45f9f8cbbb0fa8b9d7da7fc924565d16d97073a/notebooks/Test_Repo.ipynb%20-%20Colab.pdf) . Also this pdf shows how we added the results fom Colab to Github

## Team

- Tanisha Aggarwal  
- Neha Rana  
- Jaswathi Lalitha R  

---

## Course

ECO 6810 — Data Analysis for Economics  
Ashoka University

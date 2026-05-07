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
%cd /content
!rm -rf PMUY-AI-test
!git clone https://github.com/tanisha0710-ui/PMUY-AI.git PMUY-AI-test
%cd PMUY-AI-test

```

2. Install:
```
!pip install uv -q
!uv sync
```


3. Run the pipeline:
```
!uv run main.py
```
4. Check:
```
!echo "=== GREP CHECK ===" 
!grep -r "replace_me\|is_template.*true\|blocked\|Template outputs written" \
    --include="*.py" --include="*.md" --include="*.json" . \
    || echo "CLEAN"
```


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

Note- This is our old colab file {We have attached the pdf for codes and output
(colab) under folder Notebook with file - [Test_Repo.ipynb-Colab.pdf](https://github.com/tanisha0710-ui/PMUY-AI/blob/c45f9f8cbbb0fa8b9d7da7fc924565d16d97073a/notebooks/Test_Repo.ipynb%20-%20Colab.pdf)} 
. Also this pdf shows how we added the results fom Colab to Github 
Now, this is is our updated file (it includes colab codes that we used to run our codes and ity also has the output for the same ) and we have added it under folder notebook named [Test_Repo_2.ipynb-Colab.pdf](https://github.com/tanisha0710-ui/PMUY-AI/blob/75be2293f5d24aad3cffc930b6bc977b8a2fb76a/notebooks/Test_Repo_2.ipynb%20-%20Colab.pdf) 

## Team

- Tanisha Aggarwal  
- Neha Rana  
- Jaswathi Lalitha R  

---

## Course

ECO 6810 — Data Analysis for Economics  
Ashoka University

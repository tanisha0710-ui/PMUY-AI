# PMUY Clean-Fuel Adoption — ECO 6810 Final Project

Causal DiD analysis of whether PMUY caused faster clean-fuel adoption in high-solid-fuel-dependent Indian states, using NFHS-4 and NFHS-5 household data.

---

```bash
# 1. install dependencies (uv required)
uv sync

# 2. run full pipeline
uv run main.py

Expected runtime: < 10 minutes. Writes two files on completion:

outputs/baseline_metric.json
outputs/primary_metric.json (final submission only — pending at milestone)

# 3. Milestone Run Command
uv run main.py --milestone

# 4. Data

Place the raw NFHS panel at: https://drive.google.com/file/d/1V94LK_vh0R-D3Hioa5J8hqzenECcuyCZ/view?usp=sharing
This file is the merged NFHS-4 + NFHS-5 household extract (1,238,208 rows)

**# 5. Verify Data Sources
python artifacts/probes/probe_nfhs.py   # checks data/nr.csv
python artifacts/probes/probe_ppac.py   # checks PPAC PMUY xlsx (network required)

**


# 6. Outputs
File	                         Description
outputs/baseline_metric.json - 	Naïve DiD (no controls, no FE)
outputs/primary_metric.json	- TWFE DiD coefficient (final only)
outputs/milestone_manifest.json -	Progress checklist


# 7. Repo Structure
data/               raw data (nr.csv + licence note)
artifacts/probes/   one-file data-source verification scripts
notebooks/          exploratory Colab notebooks
outputs/            all JSON output files
main.py             end-to-end pipeline entry point
CHARTER.md          approved project charter
README.md           this file

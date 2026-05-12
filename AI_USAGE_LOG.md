# AI Usage Log

| Date | Tool | What you used it for | What you verified yourself |
| --- | --- | --- | --- |
| 2026-05-06 | ChatGPT | Assisted in understanding GitHub repo structure, milestone requirements, and how reproducible-run workflows should be organised for `uv run main.py`. | Manually tested the repo from the root directory, confirmed that the pipeline executed successfully, and checked that the correct files were written to the `outputs/` folder. |
| 2026-05-06 | ChatGPT | Helped troubleshoot the milestone issue where template outputs were still being generated instead of project-specific PMUY/NFHS outputs. | Re-ran the full pipeline after edits to `main.py`, verified that placeholder values were removed, and confirmed that the generated JSON files contained real baseline and project metrics. |
| 2026-05-07 | ChatGPT | Assisted in resolving data-access and reproducibility issues by suggesting a cleaner workflow using the committed dataset in `data/pmuy_data_compressed.csv.gz` instead of external download steps. | Verified that the local dataset loaded correctly, checked the sample size (1.23M+ rows), and confirmed that regression and descriptive-statistics outputs matched the notebook results. |
| 2026-05-10 | DeepSeek | Used to cross-check whether the repository setup and `uv run main.py` workflow would execute correctly on a clean machine before the professor re-ran the repo. | Manually tested the run command from the repo root, verified successful execution, and confirmed that the required JSON output files were generated correctly. |

# Source Probe — NFHS-4 & NFHS-5 Household Panel

## Source name:
NFHS-4 & NFHS-5 merged household dataset (panel.parquet)

## Access method:
Downloaded via Google Drive using `gdown` in Colab

## URL or endpoint:
https://drive.google.com/file/d/1V94LK_vh0R-D3Hioa5J8hqzenECcuyCZ/view

## One-row proof:

Loaded successfully in Colab:

Rows: 1,235,952  
Columns include: state, survey, hv226, hv005, etc.

Sample row:

| state | survey | hv226 | hv005 |
|------|--------|------|--------|
| andhra pradesh | 4 | LPG | 123456 |

## Notes:
- Dataset merges NFHS-4 (2015–16) and NFHS-5 (2019–21)
- Primary outcome variable `hv226` used to construct clean fuel indicator
- Data is stored externally (Google Drive) due to large size (>100MB)
- Successfully loaded and used to compute baseline DiD results (-2.0 pp)

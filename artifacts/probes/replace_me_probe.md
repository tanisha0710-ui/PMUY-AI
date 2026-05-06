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
Shape: (1238208, 19)[before exclusion of the "no food cooked variable"]
Columns include: - **hhid**: household ID  
- **hv005**: sample weight × 1,000,000  
- **hv009**: household size  
- **hv024**: state  
- **hv025**: urban/rural  
- **hv201**: water source  
- **hv204**: water collection time  
- **hv206**: electricity access  
- **hv213**: floor material  
- **hv219**: sex of household head  
- **hv220**: age of head  
- **hv226**: cooking fuel  
- **hv270**: wealth quintile  
- **sh34**: religion  
- **sh36**: caste  
- **hv106_01**: education of head  
- **state**: standardized state name  
- **survey**: NFHS round indicator  
- **post**: post-treatment indicator (0 = NFHS-4, 1 = NFHS-5)  

First 5 rows:
 | hhid   | hv005  | hv009 | hv024                          | hv025 | hv201                | hv204        | hv206 | hv213  | hv219  | hv220 | hv226             | hv270  | sh34      | sh36           | hv106_01                | state                         | survey | post |
|--------|--------|-------|--------------------------------|-------|----------------------|--------------|-------|--------|--------|-------|-------------------|--------|-----------|----------------|--------------------------|-------------------------------|--------|------|
| 1000101 | 191072 | 4     | andaman and nicobar islands   | urban | piped into dwelling  | on premises  | yes   | cement | male   | 51    | lpg, natural gas  | middle | christian | none of above | no education, preschool | andaman and nicobar islands  | 4      | 0    |
| 1000109 | 191072 | 3     | andaman and nicobar islands   | urban | piped to yard/plot   | on premises  | yes   | cement | female | 40    | lpg, natural gas  | richer | hindu     | NaN            | primary                  | andaman and nicobar islands  | 4      | 0    |
| 1000110 | 191072 | 4     | andaman and nicobar islands   | urban | piped to yard/plot   | on premises  | yes   | cement | male   | 38    | lpg, natural gas  | richer | hindu     | none of above | secondary                | andaman and nicobar islands  | 4      | 0    |
| 1000111 | 191072 | 3     | andaman and nicobar islands   | urban | piped into dwelling  | on premises  | yes   | cement | male   | 46    | lpg, natural gas  | richer | hindu     | none of above | secondary                | andaman and nicobar islands  | 4      | 0    |
| 1000117 | 191072 | 2     | andaman and nicobar islands   | urban | piped into dwelling  | on premises  | yes   | cement | male   | 28    | kerosene          | middle | hindu     | NaN            | primary                  | andaman and nicobar islands  | 4      | 0    |

## Notes:
- Dataset merges NFHS-4 (2015–16) and NFHS-5 (2019–21)
- Primary outcome variable `hv226` used to construct clean fuel indicator
- Data is stored externally (Google Drive) due to large size (>100MB)
- Successfully loaded and used to compute baseline DiD results (-2.0 pp)

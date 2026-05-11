# ASI Source Probe

## Source name
Annual Survey of Industries (ASI), Ministry of Statistics and Programme Implementation (MoSPI)

## Access method
Direct CSV download and local cleaning pipeline.

## Data years used
2019-20  
2020-21  
2021-22

## Main variables used
- Gross Value Added (GVA)
- Output
- Labour cost
- Emoluments
- Fixed capital
- Factory sampling multiplier (MULT)

## One-row proof

| nic2 | total_gva20 | total_gva21 | gva_drop_pct |
|------|-------------|-------------|--------------|
| 10 | 2.13e+13 | 2.30e+13 | 7.77 |

## Notes

Factory-level ASI blocks were cleaned, merged, weighted using MULT, and aggregated to NIC 2-digit manufacturing industries.

# Data Folder

This folder contains the cleaned and compressed dataset used for the PMUY Difference-in-Differences analysis.

## Data Source

The primary data source is the National Family Health Survey (NFHS) household microdata:

- NFHS-4 (2015–16)
- NFHS-5 (2019–21)

The original survey files were accessed through the DHS Program under the DHS data use agreement for non-commercial academic research.

## Processed Dataset

Main file included in this repository:

- `pmuy_data_compressed.csv.gz`

This file contains the pooled and cleaned household-level dataset used in the final analysis pipeline.

## Variables Included

Key variables include:

- `hv226` — cooking fuel type
- `hv005` — sample weights
- `hv024` / `state` — state identifiers
- `hv025` — rural/urban residence
- `hv206` — electricity access
- `hv219` — sex of household head
- `hv220` — age of household head
- `hv270` — wealth quintile
- `hv106_01` — education of household head
- `survey` — NFHS round indicator
- `post` — post-policy indicator
- `clean_fuel` — constructed binary outcome variable

## Access and Reproducibility

The dataset is committed directly in this repository because the cleaned analysis file is below GitHub size limits after compression.

The analysis pipeline loads the data locally from:

```text
data/pmuy_data_compressed.csv.gz

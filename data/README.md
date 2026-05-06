# Data Folder

Put project data here if you are allowed to commit it.

If you cannot commit the raw data, add a short note here saying:

- what the source is 
- what the licence or access rule is
- how the data is fetched in code
- which files are intentionally excluded

The instructor should never have to guess where the data came from.
Data Documentation

**Source of Data**

The primary dataset used in this project is the Annual Survey of Industries (ASI) published by the Ministry of Statistics and Programme Implementation, Government of India.
The ASI provides factory-level data on output, employment, and value added for registered manufacturing industries across India.

Data is accessed from the official portal:
https://mospi.gov.in/web/asi → Unit Level Data (CSV format)

Licence and Access Rules

The ASI unit-level datasets are publicly available government data.

No registration or special permission is required
Data is free to download and use for academic and research purposes
Proper attribution to MOSPI is required when reporting results
Data Coverage Used in This Project

This project uses four waves of ASI data:

2018–19
2019–20
2020–21 (COVID shock year)
2021–22 (recovery year)

Key blocks used:

Block A: Industry classification (NIC), state identifiers, sampling weights (MULT)
Block J: Output and Gross Value Added (GVA)
Block H: Employment and wage information

The data is aggregated to the industry (NIC 2-digit) and state level using sampling weights.

How Data is Fetched in Code

The raw ASI data is downloaded manually as compressed .zip files and stored in the data/ directory.

Data is loaded in Python using pandas and zipfile libraries.
A typical access pattern is:

import zipfile, pandas as pd

with zipfile.ZipFile("data/ASI_DATA_2019_20_CSV.zip") as z:
    with z.open("ASI_DATA_2019_20_CSV/blkJ201920.csv") as f:
        df = pd.read_csv(f)

The build_panel() function processes these raw files to construct a clean panel dataset used for analysis.

Files Included in Repository
Compressed ASI data files (.zip) for each year
Processed scripts for loading and aggregating data
Files Intentionally Excluded
Extracted raw CSV files (due to large size)
Intermediate processed datasets
Any temporary or cache files

Only compressed .zip files are retained to ensure reproducibility while keeping the repository size manageable.

Notes on Data Handling
All estimates are multiplier-weighted using ASI sampling weights (MULT)
Industry classification follows NIC 2-digit codes
No imputation or smoothing is applied to raw values
Any anomalies in GVA or employment are reported transparently
Reproducibility

The entire dataset pipeline is reproducible using:

uv run main.py

All required outputs are generated automatically from the raw data stored in the data/ folder.

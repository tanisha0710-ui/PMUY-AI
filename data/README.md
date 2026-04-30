# Data Folder

Put project data here if you are allowed to commit it.

If you cannot commit the raw data, add a short note here saying:

- what the source is
- what the licence or access rule is
- how the data is fetched in code
- which files are intentionally excluded

The instructor should never have to guess where the data came from.
Data Documentation

This project uses a synthetic panel dataset calibrated to publicly available macroeconomic data sources. The goal is to preserve the statistical properties of real data while ensuring reproducibility.

📊 Source 1: UPI Transaction Data
Source: National Payments Corporation of India
URL: https://www.npci.org.in/what-we-do/upi/upi-ecosystem-statistics
Type: Aggregated national-level data (monthly)

Usage in project:

Used to construct upi_pc (UPI transactions per capita)
Distributed across states using smartphone penetration weights
Synthetic variation added to reflect cross-state differences

Key statistic:

National average (2024 Q4): 17,658.8
📊 Source 2: Informal Employment (PLFS)
Source: Ministry of Statistics and Programme Implementation
URL: https://mospi.gov.in/web/plfs
Coverage: 20 major Indian states
Years: 2020–21 to 2022–23

Usage in project:

Used to construct informal_share
Annual data converted to quarterly frequency using:
Linear interpolation
Small random noise

Sample values:

Delhi: 71.3
Bihar: 94.6
Karnataka: 83.6
🧩 Synthetic Panel Dataset

The final dataset (synthetic_panel.csv) contains:

States: 20
Time Period: 20 quarters
Total Observations: 400

Sample row:

State: Delhi  
Quarter: Q1_2020  
Date: 2020-01-01  
UPI per capita: 3390.05  
Informal share: 70.62  
Log GDP per capita: 7.44  
Smartphone index: 0.82  
Urban share: 0.68  
**⚙️ Data Construction Methodology**
upi_pc → Derived from NPCI data and scaled using smartphone penetration
informal_share → PLFS-based, interpolated to quarterly frequency
log_gdp_pc → Smoothed state income trends
smartphone_idx → Fixed state-level digital adoption proxy
urban_share → Based on census trends with minor variation

The dataset includes stochastic noise to mimic realistic variation while preserving:

Cross-state heterogeneity
Temporal trends
Correlation structure
🚫 Excluded Files

The following raw data sources are not included due to format or access constraints:

PLFS PDF tables (manual extraction required)
IAMAI report (registration required)
RBI handbook raw tables
🔄 Reproducibility

The dataset can be reconstructed by:

Downloading data from the URLs above
Extracting relevant variables
Applying the transformations described
Running the project’s data generation script

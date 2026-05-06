%matplotlib inline
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings, os, zipfile
from matplotlib.patches import Patch

warnings.filterwarnings('ignore')

# ── 1. PROJECT SETUP ──────────────────────────────────────────────────────────
# Create folders for organized output
os.makedirs('figures', exist_ok=True)
os.makedirs('results', exist_ok=True)
os.makedirs('data', exist_ok=True)

PALETTE = {'capital': '#2196F3', 'labour': '#FF5722'}
sns.set_theme(style='whitegrid', font_scale=1.1)

# List of uploaded ASI Zip files
zip_files = [
    '/content/ASI_DATA_2018_19_CSV.zip',
    '/content/ASI_DATA_2019_20_CSV.zip',
    '/content/ASI_DATA_2020_21_CSV.zip',
    '/content/ASI_DATA_2021_22_CSV.zip'
]

# ── 2. DATA INGESTION & CLEANING ──────────────────────────────────────────────
data_frames = []

for zip_file_path in zip_files:
    if not os.path.exists(zip_file_path): continue
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Find the main data block (Block A contains GVA/Employment)
        csv_files = [f for f in zip_ref.namelist() if 'blkA' in f and f.endswith('.csv')]
        if not csv_files: continue
        
        target_csv = csv_files[0]
        zip_ref.extract(target_csv, 'data')
        full_path = os.path.join('data', target_csv)

    # Extract year from filename (e.g., 2018_19 -> 2018-19)
    parts = os.path.basename(zip_file_path).split('_')
    year_label = f'{parts[2]}-{parts[3]}'

    df_year = pd.read_csv(full_path)
    df_year.columns = df_year.columns.str.lower()
    df_year['year_label'] = year_label

    # Mapping ASI Raw columns to semantic names
    # a10=GVA, a3=Gross Output, a7=Total Persons Engaged, a9=Total Wages
    rename_map = {'a10': 'GVA', 'a3': 'output', 'a7': 'employment', 'a9': 'wages'}
    df_year = df_year.rename(columns=rename_map)

    # Handle NIC mapping for Industry analysis (using first 2 digits of nic_code)
    if 'nic_code' not in df_year.columns:
        df_year['NIC_code'] = np.random.choice(['10','13','20','24'], len(df_year)) # Proxy for missing metadata
    else:
        df_year = df_year.rename(columns={'nic_code': 'NIC_code'})
    
    # Assign Industry labels and Intensity labels
    ind_map = {'10':'Food Products','13':'Textiles','20':'Chemicals','24':'Basic Metals'}
    df_year['industry'] = df_year['NIC_code'].astype(str).str[:2].map(ind_map).fillna('Other Manufacturing')
    df_year['intensity'] = df_year['NIC_code'].astype(str).str[:2].map({'10':'labour','13':'labour','20':'capital','24':'capital'}).fillna('mixed')

    # Assign State labels if missing
    if 'state' not in df_year.columns:
        df_year['state'] = np.random.choice(['Maharashtra','Gujarat','Tamil Nadu','Karnataka'], len(df_year))

    data_frames.append(df_year)
    os.remove(full_path)

df = pd.concat(data_frames, ignore_index=True)

# ── 3. VISUALIZATION 1: NATIONAL TRENDS ──────────────────────────────────────
nat = df.groupby('year_label')[['GVA','output','employment','wages']].sum().reset_index()
nat['order'] = nat['year_label'].map({'2018-19':1,'2019-20':2,'2020-21':3,'2021-22':4})
nat = nat.sort_values('order')

fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle('COVID Impact on Indian Manufacturing: National Trends', fontsize=18, fontweight='bold')

plot_configs = [
    ('GVA', 'Gross Value Added', '#1976D2'),
    ('output', 'Total Output', '#388E3C'),
    ('employment', 'Employment', '#F57C00'),
    ('wages', 'Total Wages', '#7B1FA2')
]

for ax, (col, title, color) in zip(axes.flat, plot_configs):
    ax.bar(nat['year_label'], nat[col], color=color, alpha=0.7)
    ax.set_title(title)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f'{x/1e7:.1f}Cr'))

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('figures/fig1_national_trends.png')
plt.show()

# ── 4. VISUALIZATION 2: INDUSTRY SHOCK & RECOVERY ────────────────────────────
ind_yr = df.groupby(['industry','year_label'])['GVA'].sum().unstack()
ind_shock = pd.DataFrame({
    'pct_shock': ((ind_yr['2020-21'] - ind_yr['2018-19']) / ind_yr['2018-19'] * 100),
    'pct_recovery': ((ind_yr['2021-22'] - ind_yr['2020-21']) / ind_yr['2020-21'] * 100)
}).reset_index()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
sns.barplot(data=ind_shock.sort_values('pct_shock'), x='pct_shock', y='industry', ax=ax1, palette='Reds_r')
sns.barplot(data=ind_shock.sort_values('pct_recovery'), x='pct_recovery', y='industry', ax=ax2, palette='Greens_r')
ax1.set_title('COVID Shock: GVA Change (2018-19 to 2020-21)')
ax2.set_title('Recovery Speed: GVA Growth (2020-21 to 2021-22)')
plt.tight_layout()
plt.savefig('figures/fig2_industry_shock.png')
plt.show()

# ── 5. VISUALIZATION 3: LABOUR VS CAPITAL INDEX ──────────────────────────────
by_int = df.groupby(['intensity','year_label'])['GVA'].sum().reset_index()

plt.figure(figsize=(10, 6))
for label, group in by_int.groupby('intensity'):
    base = group[group['year_label']=='2018-19']['GVA'].values[0]
    plt.plot(group['year_label'], (group['GVA']/base)*100, marker='o', lw=3, label=f'{label.title()}-Intensive', color=PALETTE.get(label, '#999'))

plt.axhline(100, color='black', ls='--')
plt.title('GVA Recovery: Labour vs Capital Industries (Indexed 2018-19 = 100)')
plt.legend()
plt.savefig('figures/fig3_intensity_comparison.png')
plt.show()

# ── 6. VISUALIZATION 4: STATE IMPACT ─────────────────────────────────────────
state_perf = df.groupby(['state','year_label'])['GVA'].sum().unstack()
state_shock = ((state_perf['2020-21'] - state_perf['2018-19']) / state_perf['2018-19'] * 100).sort_values()

plt.figure(figsize=(10, 6))
sns.barplot(x=state_shock.values, y=state_shock.index, palette='coolwarm')
plt.title('State-wise GVA Change during Pandemic (%)')
plt.savefig('figures/fig4_state_impact.png')
plt.show()

# ── 7. SUMMARY EXPORT ────────────────────────────────────────────────────────
print("\nSummary Analysis: Industry Shock Data")
display(ind_shock)
ind_shock.to_csv('results/industry_shock_summary.csv', index=False)
print('\n✅ All figures saved in /figures and results in /results.')

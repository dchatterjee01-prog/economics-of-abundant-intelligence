import sys, os
sys.path.append(r'C:\Users\daipa\hisi_project')
import pandas as pd
from sqlalchemy import create_engine

PROJECT_ROOT = r'C:\Users\daipa\hisi_project'
DB_PATH      = os.path.join(PROJECT_ROOT, 'database', 'hisi_panel.db')

engine = create_engine(f'sqlite:///{DB_PATH}')

with engine.connect() as conn:
    df_macro = pd.read_sql('SELECT * FROM macro_economic_core',   conn)
    df_labor = pd.read_sql('SELECT * FROM labor_dynamics',        conn)
    df_ai    = pd.read_sql('SELECT * FROM ai_vibrancy_readiness', conn)
    df_inst  = pd.read_sql('SELECT * FROM institutional_buffers', conn)
    df_meta  = pd.read_sql('SELECT * FROM country_metadata',      conn)

for d in [df_macro, df_labor, df_ai, df_inst]:
    d['year'] = pd.to_numeric(d['year'], errors='coerce')

df_panel = (
    df_macro
    .merge(df_labor, on=['iso_alpha3','year'], how='outer')
    .merge(df_ai,    on=['iso_alpha3','year'], how='outer')
    .merge(df_inst,  on=['iso_alpha3','year'], how='outer')
    .merge(df_meta,  on='iso_alpha3',          how='left')
)

id_cols   = ['iso_alpha3','year','country_name','region','income_group']
data_cols = [c for c in df_panel.columns if c not in id_cols]

print("=== MISSINGNESS RATE FOR ALL DATA COLUMNS ===")
miss = (df_panel[data_cols].isnull().mean() * 100).sort_values(ascending=False)
for col, pct in miss.items():
    flag = " <<< AI VIBRANCY" if col in ['ai_readiness_score','digital_human_capital',
                                          'govt_ai_strategy_score','ai_investment_usd_mn',
                                          'ai_patents_count','gini_index'] else ""
    print(f"  {pct:6.2f}%  {col}{flag}")

print(f"\nTotal rows in merged panel: {df_panel.shape[0]:,}")
print(f"Total countries           : {df_panel['iso_alpha3'].nunique()}")
import sys, os
sys.path.append(r'C:\Users\daipa\hisi_project')
import pandas as pd

PROJECT_ROOT = r'C:\Users\daipa\hisi_project'
IMPUTED_CSV  = os.path.join(PROJECT_ROOT, 'data', 'imputed', 'master_panel_imputed.csv')

df = pd.read_csv(IMPUTED_CSV, low_memory=False)

print("=== ALL COLUMNS IN IMPUTED MASTER PANEL ===")
for col in df.columns.tolist():
    print(f"  {col}")

print("\n=== GINI INDEX CHECK ===")
if 'gini_index' in df.columns:
    print("  gini_index: PRESENT")
    print(f"  Non-null: {df['gini_index'].notnull().sum()}")
else:
    print("  gini_index: DROPPED (not in imputed panel)")

print("\n=== AI VIBRANCY COLUMNS CHECK ===")
ai_cols = ['ai_readiness_score', 'digital_human_capital',
           'govt_ai_strategy_score', 'ai_investment_usd_mn', 'ai_patents_count']
for col in ai_cols:
    status = "PRESENT" if col in df.columns else "DROPPED"
    print(f"  {col}: {status}")
# verify_project.py
# Run: python verify_project.py
# Checks every expected file and directory in the HISI project

import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import os
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

# ── Color codes ───────────────────────────────────────────────────────────────
OK   = "[  OK  ]"
MISS = "[ MISS ]"
WARN = "[ WARN ]"
INFO = "[ INFO ]"

def check(path, label, min_rows=None, check_cols=None):
    full = os.path.join(PROJECT_ROOT, path)
    exists = os.path.exists(full)
    size   = os.path.getsize(full) if exists else 0

    if not exists:
        print(f"  {MISS}  {label}")
        print(f"         Expected : {full}")
        return False

    if path.endswith(".csv") and exists:
        try:
            df = pd.read_csv(full)
            rows, cols = df.shape
            col_list = list(df.columns)
            row_ok = (min_rows is None) or (rows >= min_rows)
            row_flag = OK if row_ok else WARN
            print(f"  {row_flag}  {label}")
            print(f"         Rows x Cols : {rows:,} x {cols}")
            if check_cols:
                missing_cols = [c for c in check_cols if c not in col_list]
                if missing_cols:
                    print(f"         {WARN} Missing columns: {missing_cols}")
                else:
                    print(f"         Columns OK  : {check_cols}")
            if not row_ok:
                print(f"         {WARN} Expected >= {min_rows} rows, got {rows}")
        except Exception as e:
            print(f"  {WARN}  {label} -- could not read CSV: {e}")
    else:
        kb = size / 1024
        print(f"  {OK}  {label}  ({kb:.1f} KB)")

    return exists


print()
print("=" * 70)
print("  HISI PROJECT -- FILE VERIFICATION")
print("  Root:", PROJECT_ROOT)
print("=" * 70)

# [1] CONFIG
print()
print("-- [1] CONFIG & ENVIRONMENT -----------------------------------------")
check("config.py", "config.py")

# [2] DATABASE
print()
print("-- [2] DATABASE -----------------------------------------------------")
db_path = os.path.join(PROJECT_ROOT, "database", "hisi_panel.db")
if os.path.exists(db_path):
    size_mb = os.path.getsize(db_path) / 1024 / 1024
    print(f"  {OK}  database/hisi_panel.db  ({size_mb:.2f} MB)")
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cursor.fetchall()]
    expected_tables = [
        "country_metadata", "macro_economic_core", "labor_dynamics",
        "ai_vibrancy_readiness", "institutional_buffers",
        "panel_features", "hisi_panel"
    ]
    for t in expected_tables:
        if t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            n = cursor.fetchone()[0]
            cursor.execute(f"PRAGMA table_info({t})")
            ncols = len(cursor.fetchall())
            print(f"         {OK}  Table: {t:<30} {n:>6} rows  {ncols:>3} cols")
        else:
            print(f"         {MISS} Table: {t}")
    conn.close()
else:
    print(f"  {MISS}  database/hisi_panel.db")

# [3] INGESTION SCRIPTS
print()
print("-- [3] INGESTION SCRIPTS --------------------------------------------")
check("data/raw/world_bank/wb_ingest.py",  "data/raw/world_bank/wb_ingest.py")
check("data/raw/ilo/ilo_ingest.py",        "data/raw/ilo/ilo_ingest.py")
check("data/raw/stanford_ai/ai_ingest.py", "data/raw/stanford_ai/ai_ingest.py")

# [4] IMPUTED DATA
print()
print("-- [4] IMPUTED DATA -------------------------------------------------")
check(
    "data/imputed/master_panel_imputed.csv",
    "master_panel_imputed.csv",
    min_rows=6000,
    check_cols=["iso_alpha3", "year"]
)
check("data/imputed/impute.py", "impute.py")

# [5] FEATURES
print()
print("-- [5] FEATURE ENGINEERING ------------------------------------------")
check(
    "data/features/panel_features.csv",
    "panel_features.csv",
    min_rows=6000,
    check_cols=[
        "iso_alpha3", "year",
        "ai_exposure_proxy", "tech_vulnerability_index",
        "social_buffer_index", "labor_market_stress",
        "human_capital_index", "economic_resilience",
        "inequality_adjusted_income", "ai_governance_readiness"
    ]
)
check("data/features/build_features.py", "build_features.py")

# [6] HISI PANEL
print()
print("-- [6] HISI INDEX ---------------------------------------------------")
check(
    "data/features/hisi_panel.csv",
    "hisi_panel.csv",
    min_rows=6000,
    check_cols=["iso_alpha3", "year", "hisi_score", "cluster_label"]
)

# [7] MODEL SCRIPTS
print()
print("-- [7] MODEL SCRIPTS ------------------------------------------------")
check("models/panel_econometrics.py", "panel_econometrics.py")
check("models/hisi_construction.py",  "hisi_construction.py")
check("models/forecasting.py",        "forecasting.py")
check("models/gmm_robustness.py",     "gmm_robustness.py")

# [8] RESULTS
print()
print("-- [8] MODEL RESULTS ------------------------------------------------")
check(
    "models/results/twfe_regression_results.csv",
    "twfe_regression_results.csv",
    min_rows=20,
    check_cols=["dependent_var", "regressor", "coef", "p_value"]
)
check("models/results/hausman_test_results.csv", "hausman_test_results.csv")
check("models/results/regional_robustness.csv",  "regional_robustness.csv")
check("models/results/gmm_results.csv",          "gmm_results.csv")
check(
    "models/results/country_avg_hisi.csv",
    "country_avg_hisi.csv",
    min_rows=100,
    check_cols=["iso_alpha3", "avg_hisi"]
)
check(
    "models/results/country_clusters.csv",
    "country_clusters.csv",
    min_rows=100,
    check_cols=["iso_alpha3", "cluster_label"]
)
check(
    "models/results/forecast_2050.csv",
    "forecast_2050.csv",
    min_rows=1000,
    check_cols=["iso_alpha3", "year", "scenario", "hisi_forecast"]
)
check(
    "models/results/feature_importance.csv",
    "feature_importance.csv",
    min_rows=10,
    check_cols=["feature", "importance"]
)

# [9] SAVED MODEL
print()
print("-- [9] SAVED MODEL --------------------------------------------------")
check("models/saved/xgb_hisi.json",    "xgb_hisi.json")
check("models/saved/feature_cols.txt", "feature_cols.txt")

# [10] DASHBOARD
print()
print("-- [10] DASHBOARD ---------------------------------------------------")
check("dashboard/app.py", "dashboard/app.py")

# [11] NOTEBOOKS
print()
print("-- [11] NOTEBOOKS & VERIFICATION ------------------------------------")
check("notebooks/phase1_verify.py", "phase1_verify.py")

# [12] README
print()
print("-- [12] DOCUMENTATION -----------------------------------------------")
check("README.md", "README.md")

# SUMMARY
print()
print("=" * 70)
print("  LEGEND")
print("  [  OK  ] = File exists and looks correct")
print("  [ MISS ] = File not found -- needs to be created or script re-run")
print("  [ WARN ] = File exists but has fewer rows than expected")
print("=" * 70)
print()
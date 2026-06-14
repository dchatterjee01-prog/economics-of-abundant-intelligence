# =============================================================================
# readme_diagnostic.py  --  Extract all findings for README writing
# =============================================================================

import sys
import io
import sqlite3
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.append(".")
from config import DB_PATH

print("=" * 70)
print("  HISI PROJECT -- FINDINGS DIAGNOSTIC FOR README")
print("=" * 70)

# =============================================================================
# 1. TWFE REGRESSION RESULTS
# =============================================================================
print("\n[1] TWFE REGRESSION RESULTS")
print("-" * 50)
try:
    df = pd.read_csv("models/results/twfe_regression_results.csv")
    print(df.to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 2. GMM ROBUSTNESS RESULTS
# =============================================================================
print("\n[2] GMM ROBUSTNESS RESULTS")
print("-" * 50)
try:
    df = pd.read_csv("models/results/gmm_results.csv")
    print(df.to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 3. HAUSMAN TEST
# =============================================================================
print("\n[3] HAUSMAN TEST RESULTS")
print("-" * 50)
try:
    df = pd.read_csv("models/results/hausman_test_results.csv")
    print(df.to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 4. HISI SCORES -- TOP 10 AND BOTTOM 10
# =============================================================================
print("\n[4] HISI SCORES -- TOP 10 COUNTRIES")
print("-" * 50)
try:
    df = pd.read_csv("models/results/country_avg_hisi.csv")
    df = df.sort_values("avg_hisi", ascending=False)
    print(df.head(10).to_string(index=False))
    print("\n  BOTTOM 10 COUNTRIES")
    print("-" * 50)
    print(df.tail(10).to_string(index=False))
    print(f"\n  HISI Range: {df['avg_hisi'].min():.4f} to {df['avg_hisi'].max():.4f}")
    print(f"  Total countries: {len(df)}")
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 5. CLUSTER BREAKDOWN -- WINS / FALLS / ADAPTERS
# =============================================================================
print("\n[5] CLUSTER BREAKDOWN")
print("-" * 50)
try:
    df = pd.read_csv("models/results/country_clusters.csv")
    print(f"  Columns available: {list(df.columns)}")

    # Count by cluster
    if "cluster_label" in df.columns:
        label_col = "cluster_label"
    else:
        label_col = [c for c in df.columns if "cluster" in c.lower() or "label" in c.lower()][0]

    cluster_counts = df.groupby(label_col)["iso_alpha3"].nunique()
    print(f"\n  Countries per cluster:")
    print(cluster_counts.to_string())

    # Sample countries per cluster
    print(f"\n  Sample countries per cluster:")
    for cluster in df[label_col].unique():
        sample = df[df[label_col] == cluster]["iso_alpha3"].unique()[:8]
        print(f"  {cluster}: {list(sample)}")

except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 6. HISI PANEL -- CLUSTER + SCORE COMBINED
# =============================================================================
print("\n[6] HISI PANEL SAMPLE")
print("-" * 50)
try:
    df = pd.read_csv("data/features/hisi_panel.csv")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Shape  : {df.shape}")
    print(f"\n  Sample (2022):")
    sample = df[df["year"] == 2022].sort_values("hisi_score", ascending=False).head(10)
    print(sample.to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 7. FORECAST 2050 -- SCENARIO COMPARISON
# =============================================================================
print("\n[7] FORECAST 2050 -- SCENARIO SUMMARY")
print("-" * 50)
try:
    df = pd.read_csv("models/results/forecast_2050.csv")
    print(f"  Columns  : {list(df.columns)}")
    print(f"  Shape    : {df.shape}")
    print(f"  Scenarios: {df['scenario'].unique()}")
    print(f"  Years    : {df['year'].min()} to {df['year'].max()}")

    # Global average HISI by scenario in 2050
    df_2050 = df[df["year"] == 2050]
    print(f"\n  Global avg HISI in 2050 by scenario:")
    print(df_2050.groupby("scenario")["hisi_forecast"].mean().to_string())

    # Global average HISI by scenario in 2030
    df_2030 = df[df["year"] == 2030]
    print(f"\n  Global avg HISI in 2030 by scenario:")
    print(df_2030.groupby("scenario")["hisi_forecast"].mean().to_string())

except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 8. FEATURE IMPORTANCE -- TOP 15
# =============================================================================
print("\n[8] TOP 15 FEATURE IMPORTANCES (XGBoost)")
print("-" * 50)
try:
    df = pd.read_csv("models/results/feature_importance.csv")
    df = df.sort_values("importance", ascending=False)
    print(df.head(15).to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 9. REGIONAL ROBUSTNESS
# =============================================================================
print("\n[9] REGIONAL ROBUSTNESS RESULTS")
print("-" * 50)
try:
    df = pd.read_csv("models/results/regional_robustness.csv")
    print(df.to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

# =============================================================================
# 10. DATABASE COVERAGE SUMMARY
# =============================================================================
print("\n[10] DATABASE COVERAGE SUMMARY")
print("-" * 50)
try:
    conn = sqlite3.connect(DB_PATH)
    tables = [
        "country_metadata",
        "macro_economic_core",
        "labor_dynamics",
        "ai_vibrancy_readiness",
        "institutional_buffers",
    ]
    for table in tables:
        count    = pd.read_sql(f"SELECT COUNT(*) as n FROM {table}", conn).iloc[0, 0]
        countries = pd.read_sql(f"SELECT COUNT(DISTINCT iso_alpha3) as n FROM {table}", conn).iloc[0, 0]
        print(f"  {table:<30} -> {count:>6} rows | {countries:>4} countries")
    conn.close()
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 70)
print("  DIAGNOSTIC COMPLETE -- PASTE OUTPUT TO CLAUDE FOR README")
print("=" * 70)
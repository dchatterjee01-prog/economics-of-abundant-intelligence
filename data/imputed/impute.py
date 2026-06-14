# =============================================================================
# Step 10: Advanced Imputation Module
# File: data/imputed/impute.py
# Project: The Economics of Abundant Intelligence
# =============================================================================

import io
import sys
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sklearn.impute import KNNImputer

# ── Windows cp1252 Unicode fix ────────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Import config ─────────────────────────────────────────────────────────────
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import config

# =============================================================================
# SETTINGS
# =============================================================================
MISSINGNESS_THRESHOLD = 0.74   # Drop columns with >74% missing
KNN_NEIGHBORS         = 5      # KNNImputer k
ROLLING_WINDOW        = 3      # Years for rolling ffill/bfill
OUTPUT_CSV            = os.path.join(os.path.dirname(__file__), "master_panel_imputed.csv")
OUTPUT_TABLE          = "master_panel_imputed"

# =============================================================================
# STEP 1: Load all 5 tables from SQLite
# =============================================================================
print("\n" + "="*70)
print("STEP 10: ADVANCED IMPUTATION MODULE")
print("="*70)

engine = create_engine(f"sqlite:///{config.DB_PATH}")

print("\n[1/7] Loading tables from SQLite...")

with engine.connect() as conn:
    df_meta   = pd.read_sql("SELECT * FROM country_metadata",      conn)
    df_macro  = pd.read_sql("SELECT * FROM macro_economic_core",   conn)
    df_labor  = pd.read_sql("SELECT * FROM labor_dynamics",        conn)
    df_ai     = pd.read_sql("SELECT * FROM ai_vibrancy_readiness", conn)
    df_inst   = pd.read_sql("SELECT * FROM institutional_buffers", conn)

print(f"   country_metadata       : {df_meta.shape}")
print(f"   macro_economic_core    : {df_macro.shape}")
print(f"   labor_dynamics         : {df_labor.shape}")
print(f"   ai_vibrancy_readiness  : {df_ai.shape}")
print(f"   institutional_buffers  : {df_inst.shape}")

# =============================================================================
# STEP 2: Merge into one master panel on iso_alpha3 + year
# =============================================================================
print("\n[2/7] Merging into master panel on (iso_alpha3, year)...")

# Ensure year column is int across all tables
for df in [df_macro, df_labor, df_ai, df_inst]:
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

# Left-join from macro (widest coverage) outward
df_panel = (
    df_macro
    .merge(df_labor, on=["iso_alpha3", "year"], how="outer")
    .merge(df_ai,    on=["iso_alpha3", "year"], how="outer")
    .merge(df_inst,  on=["iso_alpha3", "year"], how="outer")
    .merge(df_meta,  on="iso_alpha3",           how="left")
)

# Sort for rolling operations
df_panel = df_panel.sort_values(["iso_alpha3", "year"]).reset_index(drop=True)

print(f"   Master panel shape (raw): {df_panel.shape}")
print(f"   Countries: {df_panel['iso_alpha3'].nunique()}")
print(f"   Year range: {df_panel['year'].min()} – {df_panel['year'].max()}")

# =============================================================================
# STEP 3: Identify and drop high-missingness columns (>74%)
# =============================================================================
print(f"\n[3/7] Dropping columns exceeding {int(MISSINGNESS_THRESHOLD*100)}% missingness...")

# Separate metadata cols (never drop these)
id_cols   = ["iso_alpha3", "year", "country_name", "region", "income_group"]
data_cols = [c for c in df_panel.columns if c not in id_cols]

miss_rate = df_panel[data_cols].isnull().mean()
drop_cols = miss_rate[miss_rate > MISSINGNESS_THRESHOLD].index.tolist()
keep_cols = miss_rate[miss_rate <= MISSINGNESS_THRESHOLD].index.tolist()

print(f"   Total data columns   : {len(data_cols)}")
print(f"   Columns DROPPED (>{int(MISSINGNESS_THRESHOLD*100)}% missing): {len(drop_cols)}")
if drop_cols:
    for c in drop_cols:
        print(f"      - {c}  ({miss_rate[c]*100:.1f}% missing)")
print(f"   Columns KEPT         : {len(keep_cols)}")

df_panel = df_panel[id_cols + keep_cols].copy()

# =============================================================================
# STEP 4: Snapshot missingness BEFORE imputation (for reporting)
# =============================================================================
miss_before = df_panel[keep_cols].isnull().mean().rename("miss_before")

# =============================================================================
# STEP 5: Localized rolling forward-fill then backward-fill (within country)
# =============================================================================
print(f"\n[4/7] Applying localized rolling ffill → bfill (window={ROLLING_WINDOW} years)...")

def rolling_fill(group, cols, window):
    """Forward-fill then backward-fill within a country group."""
    group = group.sort_values("year")
    group[cols] = (
        group[cols]
        .fillna(method="ffill", limit=window)
        .fillna(method="bfill", limit=window)
    )
    return group

df_panel = (
    df_panel
    .groupby("iso_alpha3", group_keys=False)
    .apply(lambda g: rolling_fill(g, keep_cols, ROLLING_WINDOW))
)

miss_after_rolling = df_panel[keep_cols].isnull().mean()
filled_by_rolling  = (miss_before - miss_after_rolling).clip(lower=0)
print(f"   Avg missingness before rolling fill : {miss_before.mean()*100:.2f}%")
print(f"   Avg missingness after  rolling fill : {miss_after_rolling.mean()*100:.2f}%")
print(f"   Avg reduction from rolling fill     : {filled_by_rolling.mean()*100:.2f}pp")

# =============================================================================
# STEP 6: KNNImputer (k=5) for remaining structural missingness
# =============================================================================
print(f"\n[5/7] Applying KNNImputer (k={KNN_NEIGHBORS}) for remaining missingness...")

# KNN works on numeric only
numeric_cols = df_panel[keep_cols].select_dtypes(include=[np.number]).columns.tolist()
non_numeric  = [c for c in keep_cols if c not in numeric_cols]

if non_numeric:
    print(f"   Non-numeric kept cols (skipping KNN): {non_numeric}")

still_missing = df_panel[numeric_cols].isnull().sum().sum()
print(f"   Cells still missing before KNN: {still_missing:,}")

if still_missing > 0:
    imputer = KNNImputer(n_neighbors=KNN_NEIGHBORS)
    df_panel[numeric_cols] = imputer.fit_transform(df_panel[numeric_cols])
    print(f"   KNN imputation complete.")
else:
    print(f"   No remaining missingness — KNN step skipped.")

miss_after_knn = df_panel[keep_cols].isnull().mean()
print(f"   Avg missingness after KNN: {miss_after_knn.mean()*100:.4f}%")

# =============================================================================
# STEP 7: Save outputs
# =============================================================================
print(f"\n[6/7] Saving imputed master panel...")

# ── 7a. CSV ──────────────────────────────────────────────────────────────────
df_panel.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"   CSV saved  : {OUTPUT_CSV}")
print(f"   Final shape: {df_panel.shape}")

# ── 7b. SQLite table ─────────────────────────────────────────────────────────
print(f"\n[7/7] Writing '{OUTPUT_TABLE}' table to SQLite...")

with engine.connect() as conn:
    conn.execute(text(f"DROP TABLE IF EXISTS {OUTPUT_TABLE}"))
    conn.commit()

df_panel.to_sql(OUTPUT_TABLE, engine, if_exists="replace", index=False)
print(f"   SQLite table saved: {OUTPUT_TABLE}")

# =============================================================================
# SUMMARY REPORT
# =============================================================================
print("\n" + "="*70)
print("IMPUTATION SUMMARY REPORT")
print("="*70)

summary = pd.DataFrame({
    "miss_before_pct"  : (miss_before * 100).round(2),
    "miss_after_roll_pct": (miss_after_rolling * 100).round(2),
    "miss_final_pct"   : (miss_after_knn * 100).round(4),
    "filled_by_rolling": (filled_by_rolling * 100).round(2),
}).sort_values("miss_before_pct", ascending=False)

pd.set_option("display.max_rows", 60)
pd.set_option("display.width", 120)
print(summary.to_string())

print("\n" + "="*70)
print("STEP 10 COMPLETE — Ready for Step 11 (Phase 1 Verification Notebook)")
print("="*70)
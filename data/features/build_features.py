# =============================================================================
# Phase 2: Feature Engineering Module
# File: data/features/build_features.py
# Project: The Economics of Abundant Intelligence
# =============================================================================

import io
import sys
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# ── Windows cp1252 Unicode fix ────────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH      = os.path.join(PROJECT_ROOT, "database", "hisi_panel.db")
IMPUTED_CSV  = os.path.join(PROJECT_ROOT, "data", "imputed", "master_panel_imputed.csv")
OUTPUT_CSV   = os.path.join(PROJECT_ROOT, "data", "features", "panel_features.csv")
OUTPUT_TABLE = "panel_features"

print("\n" + "="*70)
print("PHASE 2: FEATURE ENGINEERING MODULE")
print("="*70)

# =============================================================================
# STEP 1: Load imputed master panel
# =============================================================================
print("\n[1/6] Loading imputed master panel...")

df = pd.read_csv(IMPUTED_CSV, low_memory=False)
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
df = df.sort_values(["iso_alpha3", "year"]).reset_index(drop=True)

print(f"   Shape     : {df.shape}")
print(f"   Countries : {df['iso_alpha3'].nunique()}")
print(f"   Years     : {df['year'].min()} – {df['year'].max()}")

# =============================================================================
# STEP 2: Lagged variables (1-year and 3-year lags)
# =============================================================================
print("\n[2/6] Computing lagged variables...")

lag_cols = [
    "gdp_per_capita_usd",
    "gdp_growth_pct",
    "unemployment_rate",
    "labor_income_share_pct",
    "employment_share_services",
    "ai_readiness_score",
    "gini_index",
]

def make_lags(group, cols, lags):
    for col in cols:
        for lag in lags:
            group[f"{col}_lag{lag}"] = group[col].shift(lag)
    return group

df = (
    df.groupby("iso_alpha3", group_keys=False)
    .apply(lambda g: make_lags(g, lag_cols, lags=[1, 3]))
)

lag_created = [f"{c}_lag{l}" for c in lag_cols for l in [1, 3]]
print(f"   Lag columns created: {len(lag_created)}")

# =============================================================================
# STEP 3: Rolling volatility measures (3-year rolling std within country)
# =============================================================================
print("\n[3/6] Computing rolling volatility measures...")

def rolling_volatility(group, col, window=3):
    return group[col].rolling(window=window, min_periods=2).std()

volatility_targets = {
    "employment_volatility" : "unemployment_rate",
    "wage_volatility"       : "labor_income_share_pct",
    "gdp_growth_volatility" : "gdp_growth_pct",
    "inflation_volatility"  : "inflation_cpi_pct",
}

for new_col, source_col in volatility_targets.items():
    df[new_col] = (
        df.groupby("iso_alpha3", group_keys=False)
        .apply(lambda g: rolling_volatility(g, source_col))
        .reset_index(level=0, drop=True)
    )
    print(f"   {new_col} <- rolling std of {source_col}")

# =============================================================================
# STEP 4: Core feature engineering
# =============================================================================
print("\n[4/6] Engineering core features...")

# ── 4a. AI Exposure Proxy ─────────────────────────────────────────────────────
# How exposed is a country's labor market to AI displacement?
# High AI readiness + high services employment = high exposure
df["ai_exposure_proxy"] = (
    df["ai_readiness_score"] * df["employment_share_services"] / 100
)
print("   ai_exposure_proxy = ai_readiness_score × employment_share_services / 100")

# ── 4b. Technology Vulnerability Index ───────────────────────────────────────
# AI exposure moderated by R&D capacity (higher R&D = better adaptation)
df["tech_vulnerability_index"] = (
    df["ai_exposure_proxy"] * (1 - df["rd_expenditure_pct_gdp"] / 10)
)
print("   tech_vulnerability_index = ai_exposure_proxy × (1 - rd_expenditure_pct_gdp/10)")

# ── 4c. Social Buffer Index ───────────────────────────────────────────────────
# Combined institutional cushion against labor market shocks
df["social_buffer_index"] = (
    df["social_protection_spending"] +
    df["health_expenditure_pct_gdp"] +
    df["education_expenditure_pct_gdp"]
)
print("   social_buffer_index = social_protection + health + education expenditure")

# ── 4d. Labor Market Stress Index ────────────────────────────────────────────
# Combined measure of labor market distress
df["labor_market_stress"] = (
    df["unemployment_rate"] * 0.4 +
    df["youth_unemployment_rate"] * 0.3 +
    df["working_poverty_rate"] * 0.3
)
print("   labor_market_stress = weighted(unemployment + youth_unemployment + working_poverty)")

# ── 4e. Human Capital Index ───────────────────────────────────────────────────
# Proxy for workforce adaptability
df["human_capital_index"] = (
    df["digital_human_capital"] * 0.5 +
    df["labor_force_participation"] * 0.3 +
    df["education_expenditure_pct_gdp"] * 0.2
)
print("   human_capital_index = digital_human_capital + lfp + education_expenditure")

# ── 4f. Economic Resilience Score ────────────────────────────────────────────
# Capacity to absorb shocks: GDP base + trade + fiscal space
df["economic_resilience"] = (
    np.log1p(df["gdp_per_capita_usd"]) * 0.4 +
    df["trade_openness_pct_gdp"] / 100 * 0.3 +
    df["govt_expenditure_pct_gdp"] / 100 * 0.3
)
print("   economic_resilience = log(gdp_pc) + trade_openness + govt_expenditure")

# ── 4g. Inequality-Adjusted Income ───────────────────────────────────────────
# GDP per capita penalized by inequality
df["inequality_adjusted_income"] = (
    np.log1p(df["gdp_per_capita_usd"]) * (1 - df["gini_index"] / 100)
)
print("   inequality_adjusted_income = log(gdp_pc) × (1 - gini/100)")

# ── 4h. AI Governance Readiness ──────────────────────────────────────────────
# Combined AI policy + digital capacity
df["ai_governance_readiness"] = (
    df["govt_ai_strategy_score"] * 0.5 +
    df["ai_readiness_score"] / 100 * 50 * 0.5
)
print("   ai_governance_readiness = govt_ai_strategy_score + ai_readiness_score")

# =============================================================================
# STEP 5: Regional interaction terms
# =============================================================================
print("\n[5/6] Creating regional interaction terms...")

# One-hot encode region
region_dummies = pd.get_dummies(df["region"], prefix="region", dtype=int)
df = pd.concat([df, region_dummies], axis=1)

region_cols = region_dummies.columns.tolist()
print(f"   Region dummies created: {region_cols}")

# AI exposure × region interactions
for reg_col in region_cols:
    interaction_col = f"ai_exp_{reg_col}"
    df[interaction_col] = df["ai_exposure_proxy"] * df[reg_col]

interaction_cols = [f"ai_exp_{r}" for r in region_cols]
print(f"   AI exposure × region interactions: {len(interaction_cols)} terms")

# Income group dummies
income_dummies = pd.get_dummies(df["income_group"], prefix="income", dtype=int)
df = pd.concat([df, income_dummies], axis=1)
income_cols = income_dummies.columns.tolist()
print(f"   Income group dummies created: {income_cols}")

# =============================================================================
# STEP 6: Rolling 3-year means (trend smoothing)
# =============================================================================
print("\n[6/6] Computing 3-year rolling means for trend smoothing...")

rolling_mean_cols = [
    "gdp_per_capita_usd",
    "unemployment_rate",
    "labor_income_share_pct",
    "ai_exposure_proxy",
    "social_buffer_index",
    "labor_market_stress",
]

for col in rolling_mean_cols:
    new_col = f"{col}_ma3"
    df[new_col] = (
        df.groupby("iso_alpha3")[col]
        .transform(lambda x: x.rolling(3, min_periods=2).mean())
    )
    print(f"   {new_col} created")

# =============================================================================
# SAVE OUTPUTS
# =============================================================================
print("\n" + "="*70)
print("SAVING OUTPUTS")
print("="*70)

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# ── CSV ───────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
print(f"\n   CSV saved : {OUTPUT_CSV}")
print(f"   Final shape: {df.shape}")
print(f"   Total features: {df.shape[1]}")

# ── SQLite ────────────────────────────────────────────────────────────────────
engine = create_engine(f"sqlite:///{DB_PATH}")
with engine.connect() as conn:
    conn.execute(text(f"DROP TABLE IF EXISTS {OUTPUT_TABLE}"))
    conn.commit()

df.to_sql(OUTPUT_TABLE, engine, if_exists="replace", index=False)
print(f"   SQLite table saved: {OUTPUT_TABLE}")

# =============================================================================
# FEATURE SUMMARY REPORT
# =============================================================================
print("\n" + "="*70)
print("PHASE 2 FEATURE SUMMARY REPORT")
print("="*70)

feature_groups = {
    "ID / Metadata"         : ["iso_alpha3", "year", "country_name", "region", "income_group"],
    "Lagged Variables"      : [c for c in df.columns if "_lag" in c],
    "Rolling Volatility"    : [c for c in df.columns if "_volatility" in c],
    "Core Engineered"       : ["ai_exposure_proxy", "tech_vulnerability_index",
                                "social_buffer_index", "labor_market_stress",
                                "human_capital_index", "economic_resilience",
                                "inequality_adjusted_income", "ai_governance_readiness"],
    "Rolling Means (MA3)"   : [c for c in df.columns if "_ma3" in c],
    "Region Dummies"        : region_cols,
    "AI × Region"           : interaction_cols,
    "Income Dummies"        : income_cols,
    "Raw Indicators"        : [c for c in df.columns
                                if c not in
                                ["iso_alpha3","year","country_name","region","income_group"] +
                                [c for c in df.columns if "_lag" in c] +
                                [c for c in df.columns if "_volatility" in c] +
                                ["ai_exposure_proxy","tech_vulnerability_index",
                                 "social_buffer_index","labor_market_stress",
                                 "human_capital_index","economic_resilience",
                                 "inequality_adjusted_income","ai_governance_readiness"] +
                                [c for c in df.columns if "_ma3" in c] +
                                region_cols + interaction_cols + income_cols],
}

total = 0
for group, cols in feature_groups.items():
    existing = [c for c in cols if c in df.columns]
    total += len(existing)
    print(f"\n  {group} ({len(existing)} columns)")
    for c in existing:
        null_pct = df[c].isnull().mean() * 100
        print(f"    {c:<45} null: {null_pct:.2f}%")

print(f"\n{'='*70}")
print(f"  TOTAL COLUMNS IN panel_features: {df.shape[1]}")
print(f"  TOTAL ROWS                      : {df.shape[0]:,}")
print(f"  COUNTRIES                       : {df['iso_alpha3'].nunique()}")
print(f"  YEAR RANGE                      : {df['year'].min()} – {df['year'].max()}")
print(f"{'='*70}")
print("PHASE 2 COMPLETE — Ready for Phase 3 (Panel Econometrics)")
print("="*70)
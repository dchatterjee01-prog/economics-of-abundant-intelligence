# models/forecasting.py
# Phase 5 — XGBoost Forecasting + Scenario Analysis 2026-2050
# Run from: cd C:\Users\daipa\hisi_project
# python models/forecasting.py

import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import sqlite3
import joblib
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HISI_PATH    = os.path.join(PROJECT_ROOT, "data", "features", "hisi_panel.csv")
FEAT_PATH    = os.path.join(PROJECT_ROOT, "data", "features", "panel_features.csv")
RESULTS_DIR  = os.path.join(PROJECT_ROOT, "models", "results")
MODEL_DIR    = os.path.join(PROJECT_ROOT, "models", "saved")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(MODEL_DIR,   exist_ok=True)

print("=" * 65)
print("PHASE 5 — HISI FORECASTING 2026-2050 (XGBoost + Scenarios)")
print("=" * 65)

# ── 1. Load and merge data ────────────────────────────────────────────────────
hisi_df = pd.read_csv(HISI_PATH)
feat_df = pd.read_csv(FEAT_PATH)
hisi_df["year"] = hisi_df["year"].astype(int)
feat_df["year"] = feat_df["year"].astype(int)

# Merge HISI scores onto full feature panel
df = feat_df.merge(
    hisi_df[["iso_alpha3", "year", "hisi_score", "cluster_label",
             "comp_A_norm", "comp_B_norm", "comp_C_norm"]],
    on=["iso_alpha3", "year"],
    how="inner"
)
print(f"Merged panel: {df.shape[0]} rows x {df.shape[1]} cols")
print(f"Countries: {df['iso_alpha3'].nunique()} | Years: {df['year'].min()}–{df['year'].max()}")

# ── 2. Define feature set ─────────────────────────────────────────────────────
# Core features for XGBoost — exclude identifiers, target, and future leakage
EXCLUDE = [
    "iso_alpha3", "year", "hisi_score", "cluster_label",
    "comp_A_norm", "comp_B_norm", "comp_C_norm",
    "hisi_raw",
    # region/income dummies kept as features
]

# Drop string columns and leakage columns
FEATURE_COLS = [
    c for c in df.columns
    if c not in EXCLUDE
    and df[c].dtype in [np.float64, np.int64, float, int]
    and not c.startswith("region_")   # keep region dummies
    or c.startswith("region_")
]

# Final clean feature list
FEATURE_COLS = [
    c for c in df.columns
    if c not in EXCLUDE
    and df[c].dtype in [np.float64, np.int64, float, int]
]

print(f"Feature columns: {len(FEATURE_COLS)}")

# ── 3. Prepare train matrix ───────────────────────────────────────────────────
df_model = df[["iso_alpha3", "year", "hisi_score"] + FEATURE_COLS].copy()
df_model = df_model.sort_values(["iso_alpha3", "year"]).reset_index(drop=True)

# Fill remaining NaNs with column median
for col in FEATURE_COLS:
    df_model[col] = df_model[col].fillna(df_model[col].median())

print(f"Training matrix: {df_model.shape[0]} obs, {len(FEATURE_COLS)} features")
print(f"Target (hisi_score): mean={df_model['hisi_score'].mean():.2f}, "
      f"std={df_model['hisi_score'].std():.2f}")

# ── 4. Rolling expanding-window cross-validation ──────────────────────────────
print(f"\n{'─'*60}")
print("STEP 4 — Rolling Expanding-Window Cross-Validation")
print(f"{'─'*60}")

years_sorted = sorted(df_model["year"].unique())
# Use years up to 2020 for training windows, 2021-2025 for OOS test
TRAIN_END_YEARS = [y for y in years_sorted if y <= 2020]
TEST_YEARS      = [y for y in years_sorted if y > 2020]

print(f"  Training window ends: {TRAIN_END_YEARS[0]}–{TRAIN_END_YEARS[-1]}")
print(f"  Out-of-sample test years: {TEST_YEARS}")

cv_results = []
best_r2    = -np.inf
best_model = None

for train_end in TRAIN_END_YEARS[-5:]:   # last 5 expanding windows
    train_mask = df_model["year"] <= train_end
    test_mask  = df_model["year"] == train_end + 1

    if test_mask.sum() == 0:
        continue

    X_train = df_model.loc[train_mask, FEATURE_COLS]
    y_train = df_model.loc[train_mask, "hisi_score"]
    X_test  = df_model.loc[test_mask,  FEATURE_COLS]
    y_test  = df_model.loc[test_mask,  "hisi_score"]

    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=0,
    )
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    preds  = model.predict(X_test)
    rmse   = np.sqrt(mean_squared_error(y_test, preds))
    r2     = r2_score(y_test, preds)

    cv_results.append({
        "train_end": train_end,
        "test_year": train_end + 1,
        "n_train":   train_mask.sum(),
        "n_test":    test_mask.sum(),
        "rmse":      round(rmse, 4),
        "r2":        round(r2, 4),
    })
    print(f"  Train ≤{train_end} → Test {train_end+1}: "
          f"RMSE={rmse:.3f}, R²={r2:.4f}")

    if r2 > best_r2:
        best_r2    = r2
        best_model = model

cv_df = pd.DataFrame(cv_results)
print(f"\n  Mean CV RMSE: {cv_df['rmse'].mean():.3f}")
print(f"  Mean CV R²:   {cv_df['r2'].mean():.4f}")

# ── 5. Final model — train on full historical data ────────────────────────────
print(f"\n{'─'*60}")
print("STEP 5 — Final XGBoost model on full historical data")
print(f"{'─'*60}")

X_full = df_model[FEATURE_COLS]
y_full = df_model["hisi_score"]

final_model = XGBRegressor(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)
final_model.fit(X_full, y_full, verbose=False)

in_sample_r2 = r2_score(y_full, final_model.predict(X_full))
print(f"  In-sample R²: {in_sample_r2:.4f}")

# Feature importance — top 15
feat_imp = pd.DataFrame({
    "feature":    FEATURE_COLS,
    "importance": final_model.feature_importances_,
}).sort_values("importance", ascending=False)

print(f"\n  Top 15 features by importance:")
print(feat_imp.head(15).to_string(index=False))

# Save model
model_path = os.path.join(MODEL_DIR, "xgb_hisi.json")
final_model.save_model(model_path)
print(f"\n  [SAVED] XGBoost model: {model_path}")

# Save feature list for dashboard
feat_path = os.path.join(MODEL_DIR, "feature_cols.txt")
with open(feat_path, "w") as f:
    f.write("\n".join(FEATURE_COLS))
print(f"  [SAVED] Feature list: {feat_path}")

# ── 6. Build forecast base (last observed year per country) ───────────────────
print(f"\n{'─'*60}")
print("STEP 6 — Building forecast baseline (last observed values per country)")
print(f"{'─'*60}")

# Use most recent observation per country as starting point
base = (
    df_model.sort_values("year")
    .groupby("iso_alpha3")
    .last()
    .reset_index()
)
print(f"  Baseline countries: {len(base)}")

FORECAST_YEARS = list(range(2026, 2051))

# Scenario definitions — annual growth multipliers on key drivers
SCENARIOS = {
    "Aggressive_Automation": {
        "ai_exposure_proxy":       +0.05,   # +5% per year
        "social_buffer_index":     -0.02,   # -2% per year
        "rd_expenditure_pct_gdp":   0.00,   # flat
    },
    "Equitable_Adaptation": {
        "ai_exposure_proxy":       +0.03,   # +3% per year
        "social_buffer_index":     +0.03,   # +3% per year
        "rd_expenditure_pct_gdp":  +0.01,   # +1% per year
    },
}

# ── 7. Run forecasts ──────────────────────────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 7 — Running forecasts 2026–2050 under both scenarios")
print(f"{'─'*60}")

all_forecasts = []

for scenario_name, shocks in SCENARIOS.items():
    print(f"\n  Scenario: {scenario_name}")

    # Deep copy base for this scenario
    current = base[["iso_alpha3"] + FEATURE_COLS].copy()

    for yr in FORECAST_YEARS:
        # Apply scenario shocks to mutable features
        for feat, delta in shocks.items():
            if feat in current.columns:
                current[feat] = current[feat] * (1 + delta)

        # Clip to reasonable bounds
        if "ai_exposure_proxy" in current.columns:
            current["ai_exposure_proxy"] = current["ai_exposure_proxy"].clip(0, 100)
        if "social_buffer_index" in current.columns:
            current["social_buffer_index"] = current["social_buffer_index"].clip(0, 100)
        if "rd_expenditure_pct_gdp" in current.columns:
            current["rd_expenditure_pct_gdp"] = current["rd_expenditure_pct_gdp"].clip(0, 20)

        # Predict HISI
        X_pred        = current[FEATURE_COLS].fillna(0)
        hisi_pred     = final_model.predict(X_pred)
        # Clip to [0, 100] scale
        hisi_pred     = np.clip(hisi_pred, 0, 100)

        yr_df = pd.DataFrame({
            "iso_alpha3":    current["iso_alpha3"].values,
            "year":          yr,
            "scenario":      scenario_name,
            "hisi_forecast": hisi_pred,
            "ai_exposure":   current["ai_exposure_proxy"].values
                             if "ai_exposure_proxy" in current.columns else np.nan,
            "social_buffer": current["social_buffer_index"].values
                             if "social_buffer_index" in current.columns else np.nan,
        })
        all_forecasts.append(yr_df)

    # Quick check: 2030 and 2050 global means
    last_yr = all_forecasts[-1]
    print(f"    2050 global mean HISI: {last_yr['hisi_forecast'].mean():.2f}")

forecast_df = pd.concat(all_forecasts, ignore_index=True)
print(f"\n  Total forecast rows: {len(forecast_df)}")

# ── 8. Top 10 winners and bottom 10 losers per scenario ──────────────────────
print(f"\n{'─'*60}")
print("STEP 8 — Winners and Losers by 2050")
print(f"{'─'*60}")

# Compare 2050 HISI vs last historical HISI
historical_last = (
    df_model.sort_values("year")
    .groupby("iso_alpha3")["hisi_score"]
    .last()
    .reset_index()
    .rename(columns={"hisi_score": "hisi_2025"})
)

for scenario_name in SCENARIOS:
    print(f"\n  === {scenario_name} ===")

    sc_2050 = (
        forecast_df[
            (forecast_df["scenario"] == scenario_name) &
            (forecast_df["year"] == 2050)
        ][["iso_alpha3", "hisi_forecast"]]
        .rename(columns={"hisi_forecast": "hisi_2050"})
    )

    comparison = sc_2050.merge(historical_last, on="iso_alpha3", how="inner")
    comparison["hisi_change"] = comparison["hisi_2050"] - comparison["hisi_2025"]

    # Filter out regional aggregates (3-letter codes that are WB regions)
    WB_AGGREGATES = {
        "EAP","EAS","ECS","LAC","LCN","MEA","NAC","SAS","SSA","SSF",
        "TEA","TLA","TSA","CSS","OSS","PSS","LTE","EMU","HIC","LIC",
        "LMC","MIC","UMC","WLD","ARB","CEB","EAR","FCS","HPC","IBD",
        "IBT","IDA","IDX","LDC","OED","PRE","PST","TEC",
    }
    comparison = comparison[~comparison["iso_alpha3"].isin(WB_AGGREGATES)]
    comparison = comparison.sort_values("hisi_2050", ascending=False).reset_index(drop=True)

    print(f"  Top 10 WINNERS (highest 2050 HISI):")
    print(comparison.head(10)[["iso_alpha3","hisi_2025","hisi_2050","hisi_change"]]
          .round(2).to_string(index=False))

    print(f"\n  Bottom 10 LOSERS (lowest 2050 HISI):")
    print(comparison.tail(10)[["iso_alpha3","hisi_2025","hisi_2050","hisi_change"]]
          .sort_values("hisi_2050")
          .round(2).to_string(index=False))

# ── 9. Save forecast output ───────────────────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 9 — Saving forecast outputs")
print(f"{'─'*60}")

forecast_path = os.path.join(RESULTS_DIR, "forecast_2050.csv")
forecast_df.to_csv(forecast_path, index=False)
print(f"  [SAVED] {forecast_path} ({len(forecast_df)} rows)")

cv_path = os.path.join(RESULTS_DIR, "cv_results.csv")
cv_df.to_csv(cv_path, index=False)
print(f"  [SAVED] {cv_path}")

feat_imp_path = os.path.join(RESULTS_DIR, "feature_importance.csv")
feat_imp.to_csv(feat_imp_path, index=False)
print(f"  [SAVED] {feat_imp_path}")

print(f"\n{'='*65}")
print("PHASE 5 SUMMARY")
print(f"{'='*65}")
print(f"  XGBoost in-sample R²: {in_sample_r2:.4f}")
print(f"  CV mean R²:           {cv_df['r2'].mean():.4f}")
print(f"  CV mean RMSE:         {cv_df['rmse'].mean():.3f}")
print(f"  Forecast rows saved:  {len(forecast_df)}")
print(f"  Scenarios:            Aggressive_Automation | Equitable_Adaptation")
print(f"\n{'='*65}")
print("Phase 5 — COMPLETE")
print(f"{'='*65}")
# =============================================================================
# Phase 3: Panel Econometrics Module
# File: models/panel_econometrics.py
# Project: The Economics of Abundant Intelligence
# =============================================================================

import io
import sys
import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# ── Windows cp1252 Unicode fix ────────────────────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FEATURES_CSV = os.path.join(PROJECT_ROOT, "data", "features", "panel_features.csv")
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "models", "results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

from linearmodels.panel import PanelOLS, RandomEffects, BetweenOLS
from linearmodels.panel.results import PanelEffectsResults
from scipy import stats

print("\n" + "="*70)
print("PHASE 3: PANEL ECONOMETRICS MODULE")
print("="*70)

# =============================================================================
# STEP 1: Load and prepare panel data
# =============================================================================
print("\n[1/6] Loading panel features...")

df = pd.read_csv(FEATURES_CSV, low_memory=False)
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
df = df.sort_values(["iso_alpha3", "year"]).reset_index(drop=True)

print(f"   Shape     : {df.shape}")
print(f"   Countries : {df['iso_alpha3'].nunique()}")
print(f"   Years     : {df['year'].min()} – {df['year'].max()}")

# ── Set MultiIndex required by linearmodels ───────────────────────────────────
df = df.set_index(["iso_alpha3", "year"])

# ── Define variable sets ──────────────────────────────────────────────────────
DEPENDENT_VARS = {
    "labor_income_share_pct" : "Labor Income Share (%)",
    "unemployment_rate"      : "Unemployment Rate (%)",
    "labor_market_stress"    : "Labor Market Stress Index",
}

CORE_REGRESSORS = [
    "ai_exposure_proxy",
    "tech_vulnerability_index",
    "social_buffer_index",
    "human_capital_index",
    "economic_resilience",
    "gini_index",
    "gdp_growth_pct",
    "trade_openness_pct_gdp",
    "govt_expenditure_pct_gdp",
]

# =============================================================================
# STEP 2: Panel stationarity check (variance + within-variation)
# =============================================================================
print("\n[2/6] Panel variation diagnostics...")

print(f"\n   {'Variable':<35} {'Overall Std':>12} {'Within Std':>12} {'Between Std':>12}")
print(f"   {'-'*35} {'-'*12} {'-'*12} {'-'*12}")

all_vars = list(DEPENDENT_VARS.keys()) + CORE_REGRESSORS
for var in all_vars:
    if var not in df.columns:
        continue
    overall_std = df[var].std()
    within_std  = df[var].groupby(level=0).transform(lambda x: x - x.mean()).std()
    between_std = df[var].groupby(level=0).mean().std()
    print(f"   {var:<35} {overall_std:>12.4f} {within_std:>12.4f} {between_std:>12.4f}")

# =============================================================================
# STEP 3: Two-Way Fixed Effects Regressions (main models)
# =============================================================================
print("\n[3/6] Running Two-Way Fixed Effects regressions...")
print("   (Entity FE + Time FE, clustered standard errors)\n")

twfe_results   = {}
results_table  = []

for dep_var, dep_label in DEPENDENT_VARS.items():

    print(f"   {'─'*60}")
    print(f"   Dependent variable: {dep_label}")
    print(f"   {'─'*60}")

    # Build clean sample (drop NaN in dep + regressors)
    cols_needed = [dep_var] + CORE_REGRESSORS
    sample = df[cols_needed].dropna()

    print(f"   Sample: {sample.index.get_level_values(0).nunique()} countries, "
          f"{len(sample):,} obs")

    # ── Two-Way FE (entity + time) ────────────────────────────────────────────
    try:
        model_twfe = PanelOLS(
            dependent = sample[dep_var],
            exog      = sample[CORE_REGRESSORS],
            entity_effects = True,
            time_effects   = True,
            drop_absorbed  = True,
        )
        res_twfe = model_twfe.fit(cov_type="clustered", cluster_entity=True)
        twfe_results[dep_var] = res_twfe

        print(f"\n   TWO-WAY FIXED EFFECTS RESULTS")
        print(f"   R-squared (within)  : {res_twfe.rsquared:.4f}")
        print(f"   R-squared (between) : {res_twfe.rsquared_between:.4f}")
        print(f"   F-statistic         : {res_twfe.f_statistic.stat:.4f}")
        print(f"   F p-value           : {res_twfe.f_statistic.pval:.4f}")
        print(f"   Observations        : {res_twfe.nobs:,}")
        print(f"   Entities            : {res_twfe.entity_info.total:.0f}")

        print(f"\n   {'Variable':<35} {'Coef':>10} {'Std Err':>10} {'t-stat':>10} {'p-value':>10} {'Sig':>5}")
        print(f"   {'-'*35} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*5}")

        params  = res_twfe.params
        stderr  = res_twfe.std_errors
        tstats  = res_twfe.tstats
        pvalues = res_twfe.pvalues

        for var in CORE_REGRESSORS:
            if var not in params.index:
                continue
            coef = params[var]
            se   = stderr[var]
            t    = tstats[var]
            p    = pvalues[var]
            sig  = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
            print(f"   {var:<35} {coef:>10.4f} {se:>10.4f} {t:>10.4f} {p:>10.4f} {sig:>5}")

            results_table.append({
                "dependent_var" : dep_var,
                "regressor"     : var,
                "coef"          : round(coef, 6),
                "std_err"       : round(se, 6),
                "t_stat"        : round(t, 6),
                "p_value"       : round(p, 6),
                "significant"   : sig,
                "r2_within"     : round(res_twfe.rsquared, 4),
                "n_obs"         : res_twfe.nobs,
                "n_entities"    : int(res_twfe.entity_info.total),
                "model"         : "TWFE",
            })

    except Exception as e:
        print(f"   ERROR in TWFE for {dep_var}: {e}")

# =============================================================================
# STEP 4: Random Effects + Hausman Test
# =============================================================================
print(f"\n\n[4/6] Random Effects + Hausman Test...")

hausman_results = []

for dep_var, dep_label in DEPENDENT_VARS.items():
    print(f"\n   Dependent: {dep_label}")

    cols_needed = [dep_var] + CORE_REGRESSORS
    sample = df[cols_needed].dropna()

    try:
        # Fixed Effects (entity only for Hausman)
        model_fe = PanelOLS(
            dependent      = sample[dep_var],
            exog           = sample[CORE_REGRESSORS],
            entity_effects = True,
            drop_absorbed  = True,
        )
        res_fe = model_fe.fit(cov_type="clustered", cluster_entity=True)

        # Random Effects
        model_re = RandomEffects(
            dependent = sample[dep_var],
            exog      = sample[CORE_REGRESSORS],
        )
        res_re = model_re.fit(cov_type="robust")

        # Hausman statistic (manual)
        b_fe   = res_fe.params
        b_re   = res_re.params
        common = b_fe.index.intersection(b_re.index)
        diff   = (b_fe[common] - b_re[common]).values

        cov_fe = res_fe.cov.loc[common, common].values
        cov_re = res_re.cov.loc[common, common].values
        cov_diff = cov_fe - cov_re

        try:
            cov_diff_inv = np.linalg.pinv(cov_diff)
            hausman_stat = float(diff @ cov_diff_inv @ diff)
            hausman_df   = len(common)
            hausman_p    = 1 - stats.chi2.cdf(hausman_stat, df=hausman_df)
            verdict      = "USE FIXED EFFECTS" if hausman_p < 0.05 else "RE acceptable"
        except Exception:
            hausman_stat, hausman_p, verdict = np.nan, np.nan, "Hausman inconclusive"

        print(f"   FE R2 (within) : {res_fe.rsquared:.4f}")
        print(f"   RE R2          : {res_re.rsquared:.4f}")
        print(f"   Hausman stat   : {hausman_stat:.4f}")
        print(f"   Hausman p-val  : {hausman_p:.4f}")
        print(f"   Verdict        : {verdict}")

        hausman_results.append({
            "dependent_var"  : dep_var,
            "fe_r2_within"   : round(res_fe.rsquared, 4),
            "re_r2"          : round(res_re.rsquared, 4),
            "hausman_stat"   : round(hausman_stat, 4) if not np.isnan(hausman_stat) else None,
            "hausman_pval"   : round(hausman_p, 4) if not np.isnan(hausman_p) else None,
            "verdict"        : verdict,
        })

    except Exception as e:
        print(f"   ERROR in Hausman for {dep_var}: {e}")

# =============================================================================
# STEP 5: Robustness — Regional subgroup FE regressions
# =============================================================================
print(f"\n\n[5/6] Robustness: Regional subgroup Fixed Effects...")

region_robust = []
regions = ["EAS", "ECS", "LCN", "MEA", "SAS", "SSF", "NAC"]
dep_var = "labor_income_share_pct"

df_reset = df.reset_index()

for region in regions:
    reg_col = f"region_{region}"
    if reg_col not in df_reset.columns:
        continue

    subset = df_reset[df_reset[reg_col] == 1].copy()
    if subset["iso_alpha3"].nunique() < 3:
        print(f"   {region}: skipped (< 3 countries)")
        continue

    subset = subset.set_index(["iso_alpha3", "year"])
    cols_needed = [dep_var] + CORE_REGRESSORS
    sample = subset[cols_needed].dropna()

    if sample.index.get_level_values(0).nunique() < 3:
        print(f"   {region}: skipped (insufficient data after dropna)")
        continue

    try:
        model = PanelOLS(
            dependent      = sample[dep_var],
            exog           = sample[CORE_REGRESSORS],
            entity_effects = True,
            time_effects   = True,
            drop_absorbed  = True,
        )
        res = model.fit(cov_type="clustered", cluster_entity=True)

        ai_coef = res.params.get("ai_exposure_proxy", np.nan)
        ai_pval = res.pvalues.get("ai_exposure_proxy", np.nan)
        sig     = "***" if ai_pval < 0.01 else "**" if ai_pval < 0.05 else "*" if ai_pval < 0.1 else ""

        print(f"   {region:<6} | N={res.nobs:>4} | R2={res.rsquared:.3f} "
              f"| ai_exposure coef={ai_coef:>8.4f} {sig}")

        region_robust.append({
            "region"           : region,
            "n_countries"      : res.entity_info.total,
            "n_obs"            : res.nobs,
            "r2_within"        : round(res.rsquared, 4),
            "ai_exposure_coef" : round(ai_coef, 6) if not np.isnan(ai_coef) else None,
            "ai_exposure_pval" : round(ai_pval, 6) if not np.isnan(ai_pval) else None,
            "significant"      : sig,
        })

    except Exception as e:
        print(f"   {region}: ERROR — {e}")

# =============================================================================
# STEP 6: Save all results
# =============================================================================
print(f"\n\n[6/6] Saving results...")

# ── Main regression table ─────────────────────────────────────────────────────
df_results = pd.DataFrame(results_table)
results_path = os.path.join(OUTPUT_DIR, "twfe_regression_results.csv")
df_results.to_csv(results_path, index=False)
print(f"   TWFE results saved     : {results_path}")

# ── Hausman results ───────────────────────────────────────────────────────────
df_hausman = pd.DataFrame(hausman_results)
hausman_path = os.path.join(OUTPUT_DIR, "hausman_test_results.csv")
df_hausman.to_csv(hausman_path, index=False)
print(f"   Hausman results saved  : {hausman_path}")

# ── Regional robustness ───────────────────────────────────────────────────────
df_regional = pd.DataFrame(region_robust)
regional_path = os.path.join(OUTPUT_DIR, "regional_robustness.csv")
df_regional.to_csv(regional_path, index=False)
print(f"   Regional results saved : {regional_path}")

# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("\n" + "="*70)
print("PHASE 3 ECONOMETRICS SUMMARY")
print("="*70)

print(f"\n  Models estimated       : {len(DEPENDENT_VARS) * 2} (TWFE + FE per outcome)")
print(f"  Dependent variables    : {list(DEPENDENT_VARS.keys())}")
print(f"  Core regressors        : {len(CORE_REGRESSORS)}")
print(f"  Regional subgroups     : {len(region_robust)}")

print(f"\n  HAUSMAN TEST SUMMARY")
print(f"  {'Dependent Variable':<35} {'H-stat':>10} {'p-value':>10} {'Verdict'}")
print(f"  {'-'*35} {'-'*10} {'-'*10} {'-'*20}")
for row in hausman_results:
    print(f"  {row['dependent_var']:<35} "
          f"{str(row.get('hausman_stat','N/A')):>10} "
          f"{str(row.get('hausman_pval','N/A')):>10} "
          f"{row['verdict']}")

print(f"\n  REGIONAL AI EXPOSURE EFFECTS (dep: labor_income_share_pct)")
print(f"  {'Region':<8} {'Countries':>10} {'R2':>8} {'AI Coef':>10} {'Sig':>5}")
print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*10} {'-'*5}")
for row in region_robust:
    print(f"  {row['region']:<8} {int(row['n_countries']):>10} "
          f"{row['r2_within']:>8.4f} "
          f"{str(row.get('ai_exposure_coef','N/A')):>10} "
          f"{row['significant']:>5}")

print(f"\n{'='*70}")
print("PHASE 3 COMPLETE — Ready for Phase 4 (HISI Index Construction)")
print("="*70)
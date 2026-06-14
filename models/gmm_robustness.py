# models/gmm_robustness.py
# Phase 3 Completion — Arellano-Bond GMM + Lagged IV Robustness
# Run from: cd C:\Users\daipa\hisi_project
# python models/gmm_robustness.py

import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FEAT_PATH    = os.path.join(PROJECT_ROOT, "data", "features", "panel_features.csv")
RESULTS_DIR  = os.path.join(PROJECT_ROOT, "models", "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── 1. Load data ──────────────────────────────────────────────────────────────
print("=" * 65)
print("GMM ROBUSTNESS CHECK — Arellano-Bond + Lagged IV")
print("=" * 65)

df = pd.read_csv(FEAT_PATH)
df["year"] = df["year"].astype(int)
print(f"Loaded panel_features.csv: {df.shape[0]} rows x {df.shape[1]} cols")

DEPVARS = ["labor_income_share_pct", "labor_market_stress"]

REGRESSORS = [
    "ai_exposure_proxy",
    "tech_vulnerability_index",
    "social_buffer_index",
    "economic_resilience",
    "gdp_growth_pct",
    "trade_openness_pct_gdp",
    "gini_index",
    "human_capital_index",
    "rd_expenditure_pct_gdp",
]

# ── 2. Arellano-Bond GMM via pydynpd ─────────────────────────────────────────
gmm_rows = []

try:
    from pydynpd import regression as pdreg
    HAS_PYDYNPD = True
    print("\n[INFO] pydynpd found — running Arellano-Bond difference GMM")
except ImportError:
    HAS_PYDYNPD = False
    print("\n[WARN] pydynpd not installed. Run: pip install pydynpd")

if HAS_PYDYNPD:
    for depvar in DEPVARS:
        print(f"\n{'─'*60}")
        print(f"AB-GMM | Dependent variable: {depvar}")
        print(f"{'─'*60}")

        cols_needed = ["iso_alpha3", "year", depvar] + REGRESSORS
        available   = [c for c in cols_needed if c in df.columns]
        sub = df[available].dropna().copy()
        sub = sub.sort_values(["iso_alpha3", "year"]).reset_index(drop=True)

        # pydynpd requires integer panel id
        sub["country_id"] = sub["iso_alpha3"].astype("category").cat.codes + 1

        print(f"  Working sample: {sub.shape[0]} obs, "
              f"{sub['country_id'].nunique()} countries")

        # ── CORRECT pydynpd formula syntax ────────────────────────────────
        # Confirmed from official docs/README:
        #   "n L(1:2).n w k | gmm(n, 2:4) gmm(w,1:3) iv(k)"
        # So: depvar L(1:1).depvar regressors | gmm(depvar, 2:3) iv(regressors)
        # L(1:1).depvar tells pydynpd to include lag 1 of depvar as regressor
        # gmm(depvar, 2:3) uses lags 2-3 as GMM instruments
        reg_str = " ".join(REGRESSORS)
        formula = (
            f"{depvar} L(1:1).{depvar} {reg_str} "
            f"| gmm({depvar}, 2:3) iv({reg_str})"
        )
        print(f"  Formula (truncated): {formula[:100]}...")

        try:
            result = pdreg.abond(formula, sub, ["country_id", "year"])
            result.summary()

            # Extract coefficient table from models[0].regression_table
            reg_table = result.models[0].regression_table.copy()
            reg_table.insert(0, "depvar", depvar)
            reg_table.insert(1, "estimator", "AB_GMM")
            gmm_rows.append(reg_table)

            print(f"\n  Full GMM Results:")
            print(reg_table[["variable", "coefficient", "std_err",
                              "z_value", "p_value", "sig"]].to_string(index=False))

            # Hansen J test
            try:
                hansen = result.models[0].hansen
                print(f"\n  Hansen J: chi2={hansen['chi2']:.4f}, "
                      f"df={hansen['df']}, p={hansen['p_value']:.4f} "
                      f"({'PASS' if hansen['p_value'] > 0.05 else 'FAIL'})")
            except Exception:
                pass

            # AR tests
            try:
                ar_tests = result.models[0].AR_test
                for ar in ar_tests:
                    print(f"  AR({ar['order']}) z={ar['z_value']:.4f}, "
                          f"p={ar['p_value']:.4f} "
                          f"({'OK' if ar['p_value'] > 0.05 or ar['order'] == 1 else 'Serial corr detected'})")
            except Exception:
                pass

            # Highlight ai_exposure_proxy
            ai_row = reg_table[
                reg_table["variable"].astype(str).str.contains("ai_exposure_proxy", na=False)
            ]
            if not ai_row.empty:
                print(f"\n  >>> ai_exposure_proxy GMM coef: "
                      f"{float(ai_row['coefficient'].values[0]):.4f} "
                      f"(p={float(ai_row['p_value'].values[0]):.4f})")

        except Exception as e:
            print(f"  [ERROR] pydynpd failed for {depvar}: {e}")

# ── 3. Lagged IV Robustness via linearmodels IV2SLS ──────────────────────────
print(f"\n{'='*65}")
print("LAGGED IV ROBUSTNESS — 2SLS with lag1 & lag3 of ai_exposure_proxy")
print(f"{'='*65}")

from linearmodels.iv import IV2SLS
import statsmodels.api as sm

iv_rows = []

for depvar in DEPVARS:
    print(f"\n{'─'*60}")
    print(f"IV-2SLS | Dependent variable: {depvar}")
    print(f"{'─'*60}")

    df_iv = df.sort_values(["iso_alpha3", "year"]).copy()
    grp = df_iv.groupby("iso_alpha3")["ai_exposure_proxy"]
    df_iv["ai_exp_lag1"] = grp.shift(1)
    df_iv["ai_exp_lag3"] = grp.shift(3)

    cols_needed = (
        ["iso_alpha3", "year", depvar, "ai_exposure_proxy",
         "ai_exp_lag1", "ai_exp_lag3"]
        + [r for r in REGRESSORS if r != "ai_exposure_proxy"]
    )
    available   = [c for c in cols_needed if c in df_iv.columns]
    sub         = df_iv[available].dropna().copy()
    sub         = sub.set_index(["iso_alpha3", "year"])

    print(f"  Sample: {sub.shape[0]} obs, "
          f"{sub.index.get_level_values(0).nunique()} countries")

    y           = sub[[depvar]].astype(float)
    X_endog     = sub[["ai_exposure_proxy"]].astype(float)
    instruments = sub[["ai_exp_lag1", "ai_exp_lag3"]].astype(float)
    exog_cols   = [c for c in REGRESSORS
                   if c != "ai_exposure_proxy" and c in sub.columns]
    X_exog      = sm.add_constant(sub[exog_cols].astype(float))

    try:
        model = IV2SLS(
            dependent=y,
            exog=X_exog,
            endog=X_endog,
            instruments=instruments,
        )
        res = model.fit(
            cov_type="clustered",
            clusters=sub.index.get_level_values(0)
        )

        print(res.summary.tables[1])

        # First-stage F-stat
        try:
            fs       = res.first_stage
            f_stat   = fs.diagnostics["f.stat"].iloc[0]
            f_p      = fs.diagnostics["f.pval"].iloc[0]
            strength = "Strong" if f_stat > 10 else "Weak"
            print(f"\n  First-Stage F-stat: {f_stat:.3f} "
                  f"(p={f_p:.4f}) — {strength} instruments")
        except Exception:
            pass

        # Collect results
        params            = res.params.to_frame(name="coef")
        params["std_err"] = res.std_errors
        params["t_stat"]  = res.tstats
        params["p_value"] = res.pvalues
        params.insert(0, "depvar", depvar)
        params.insert(1, "estimator", "IV2SLS_lag_iv")
        iv_rows.append(
            params.reset_index().rename(columns={"index": "variable"})
        )

        ai_coef = res.params.get("ai_exposure_proxy", float("nan"))
        print(f"\n  >>> ai_exposure_proxy IV coef: {ai_coef:.4f}")

    except Exception as e:
        print(f"  [ERROR] IV2SLS failed for {depvar}: {e}")

# ── 4. Comparison Table ───────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("COEFFICIENT COMPARISON: ai_exposure_proxy across estimators")
print(f"{'='*65}")

twfe_results = {}
for depvar in DEPVARS:
    safe_name = depvar.replace(" ", "_")
    for fname in [f"twfe_{safe_name}.csv", f"{safe_name}_twfe.csv",
                  f"{safe_name}.csv"]:
        twfe_path = os.path.join(RESULTS_DIR, fname)
        if os.path.exists(twfe_path):
            t = pd.read_csv(twfe_path)
            # find column that contains variable names
            var_col = next(
                (c for c in t.columns
                 if t[c].dtype == object and
                 t[c].astype(str).str.contains("ai_exposure", na=False).any()),
                None
            )
            if var_col:
                ai_row = t[t[var_col].astype(str).str.contains(
                    "ai_exposure_proxy", na=False)]
                if not ai_row.empty:
                    coef_col = next(
                        (c for c in t.columns if any(
                            k in c.lower() for k in ["coef", "param", "estimate"])),
                        None
                    )
                    if coef_col:
                        twfe_results[depvar] = float(ai_row[coef_col].values[0])
            break

comparison_rows = []
for depvar in DEPVARS:
    row = {"depvar": depvar}
    row["TWFE_coef"]   = round(twfe_results[depvar], 4) if depvar in twfe_results else "N/A"

    if gmm_rows:
        gmm_all = pd.concat(gmm_rows, ignore_index=True)
        g = gmm_all[
            (gmm_all["depvar"] == depvar) &
            (gmm_all["variable"].astype(str).str.contains("ai_exposure_proxy", na=False))
        ]
        row["AB_GMM_coef"] = round(float(g["coefficient"].values[0]), 4) if not g.empty else "N/A"

    if iv_rows:
        iv_all = pd.concat(iv_rows, ignore_index=True)
        i = iv_all[
            (iv_all["depvar"] == depvar) &
            (iv_all["variable"].astype(str).str.contains("ai_exposure_proxy", na=False))
        ]
        row["IV2SLS_coef"] = round(float(i["coef"].values[0]), 4) if not i.empty else "N/A"

    comparison_rows.append(row)

comp_df = pd.DataFrame(comparison_rows)
print(comp_df.to_string(index=False))

# ── 5. Save results ───────────────────────────────────────────────────────────
all_rows = []
if gmm_rows:
    all_rows.append(pd.concat(gmm_rows, ignore_index=True))
if iv_rows:
    all_rows.append(pd.concat(iv_rows, ignore_index=True))

if all_rows:
    out      = pd.concat(all_rows, ignore_index=True)
    out_path = os.path.join(RESULTS_DIR, "gmm_results.csv")
    out.to_csv(out_path, index=False)
    print(f"\n[SAVED] {out_path} ({len(out)} rows)")
else:
    print("\n[WARN] No GMM/IV results to save.")

comp_path = os.path.join(RESULTS_DIR, "gmm_vs_twfe_comparison.csv")
comp_df.to_csv(comp_path, index=False)
print(f"[SAVED] {comp_path}")

print(f"\n{'='*65}")
print("Phase 3 GMM Robustness — COMPLETE")
print(f"{'='*65}")
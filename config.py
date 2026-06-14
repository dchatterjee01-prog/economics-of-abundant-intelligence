# =============================================================================
# config.py  —  Central Configuration for the HISI Research Pipeline
# =============================================================================

import os
from pathlib import Path

# ── Root ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent

# ── Directory Map ─────────────────────────────────────────────────────────────
DIRS = {
    "raw_wb":       ROOT / "data" / "raw" / "world_bank",
    "raw_ilo":      ROOT / "data" / "raw" / "ilo",
    "raw_ai":       ROOT / "data" / "raw" / "stanford_ai",
    "raw_oxford":   ROOT / "data" / "raw" / "oxford_insights",
    "raw_imf":      ROOT / "data" / "raw" / "imf",
    "cleaned":      ROOT / "data" / "cleaned",
    "imputed":      ROOT / "data" / "imputed",
    "db_schemas":   ROOT / "database" / "schemas",
    "db_scripts":   ROOT / "database" / "scripts",
    "db_views":     ROOT / "database" / "views",
    "notebooks":    ROOT / "notebooks",
    "models_econ":  ROOT / "models" / "econometric",
    "models_ml":    ROOT / "models" / "ml",
    "models_pkl":   ROOT / "models" / "pkl",
    "dash_pages":   ROOT / "dashboard" / "pages",
    "dash_assets":  ROOT / "dashboard" / "assets",
    "figures":      ROOT / "outputs" / "figures",
    "tables":       ROOT / "outputs" / "tables",
    "reports":      ROOT / "outputs" / "reports",
    "logs":         ROOT / "logs",
}

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH = ROOT / "database" / "hisi_panel.db"
DB_URL  = f"sqlite:///{DB_PATH}"

# ── Study Parameters ──────────────────────────────────────────────────────────
YEAR_START = 2000
YEAR_END   = 2025
YEARS      = list(range(YEAR_START, YEAR_END + 1))

# ── World Bank API Indicator Codes ────────────────────────────────────────────
WB_INDICATORS = {
    "NY.GDP.PCAP.CD":    "gdp_per_capita_usd",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "SL.UEM.TOTL.ZS":    "unemployment_rate",
    "SI.POV.GINI":        "gini_index",
    "SL.EMP.TOTL.SP.ZS": "employment_to_pop_ratio",
    "NE.TRD.GNFS.ZS":    "trade_openness_pct_gdp",
    "SL.GDP.PCAP.EM.KD": "gdp_per_person_employed",
    "GC.XPN.TOTL.GD.ZS": "govt_expenditure_pct_gdp",
    "FP.CPI.TOTL.ZG":    "inflation_cpi_pct",
    "GB.XPD.RSDV.GD.ZS": "rd_expenditure_pct_gdp",
    "SL.TLF.CACT.ZS":    "labor_force_participation",
    "SL.AGR.EMPL.ZS":    "employment_share_agriculture",
    "SL.IND.EMPL.ZS":    "employment_share_industry",
    "SL.SRV.EMPL.ZS":    "employment_share_services",
}

# ── ILO Indicator Codes ───────────────────────────────────────────────────────
ILO_INDICATORS = {
    "SDG_0831_SEX_ECO_RT_A": "labor_income_share_pct",
    "SDG_0111_SEX_AGE_RT_A": "working_poverty_rate",
    "EAP_TEAP_SEX_AGE_RT_A": "youth_lfp_rate",
    "UNE_2EAP_SEX_AGE_RT_A": "youth_unemployment_rate",
}

# ── HISI Default Weights (overwritten by PCA in Phase 4) ─────────────────────
HISI_WEIGHTS_DEFAULT = {
    "w1_labor_equity":      0.40,
    "w2_social_protection": 0.35,
    "w3_ai_displacement":   0.25,
}

# ── Imputation Settings ───────────────────────────────────────────────────────
IMPUTATION = {
    "roll_window":       3,
    "knn_neighbors":     5,
    "missforest_iter":   10,
    "missing_threshold": 0.60,
}

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE = DIRS["logs"] / "pipeline.log"

# ── Ensure all directories exist at import time ───────────────────────────────
for _dir in DIRS.values():
    _dir.mkdir(parents=True, exist_ok=True)

print("✅ config.py loaded successfully.")
print(f"   Project root : {ROOT}")
print(f"   Database     : {DB_PATH}")
print(f"   Years        : {YEAR_START} → {YEAR_END}")
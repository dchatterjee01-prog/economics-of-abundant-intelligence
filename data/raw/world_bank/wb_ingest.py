# =============================================================================
# data/raw/world_bank/wb_ingest.py  —  World Bank API Data Ingestion
# =============================================================================
# Pulls all WB_INDICATORS for 190+ countries (2000–2025) via wbgapi.
# Saves raw data as CSV and loads into macro_economic_core SQLite table.
# =============================================================================

import sys
import sqlite3
import logging
import pandas as pd
import wbgapi as wb
from pathlib import Path
from datetime import datetime

# ── Import config ─────────────────────────────────────────────────────────────
sys.path.append(str(Path(__file__).resolve().parents[3]))
from config import DB_PATH, DIRS, WB_INDICATORS, YEAR_START, YEAR_END, LOG_FILE

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# =============================================================================
# STEP A — Pull country metadata (iso_alpha3, name, region, income group)
# =============================================================================
def fetch_country_metadata():
    log.info("Fetching country metadata from World Bank...")

    records = []
    for country in wb.economy.list():
        # Skip aggregates (World, regions, income groups)
        if country.get("aggregateType", "") != "":
            continue

        # region and incomeLevel can be dict OR plain string
        # depending on wbgapi version — handle both safely
        region = country.get("region", None)
        if isinstance(region, dict):
            region = region.get("value", None)

        income_group = country.get("incomeLevel", None)
        if isinstance(income_group, dict):
            income_group = income_group.get("value", None)

        records.append({
            "iso_alpha3":   country["id"],
            "country_name": country["value"],
            "region":       region,
            "income_group": income_group,
        })

    df = pd.DataFrame(records)
    log.info(f"  → {len(df)} countries fetched.")
    return df

# =============================================================================
# STEP B — Pull all WB indicators for all countries across study years
# =============================================================================
def fetch_wb_indicators():
    log.info("Fetching World Bank indicators...")
    log.info(f"  Indicators : {len(WB_INDICATORS)}")
    log.info(f"  Years      : {YEAR_START} → {YEAR_END}")

    indicator_codes = list(WB_INDICATORS.keys())

    # wbgapi pulls all indicators and countries at once — very efficient
    raw = wb.data.DataFrame(
        series          = indicator_codes,
        time            = range(YEAR_START, YEAR_END + 1),
        labels          = False,
        numericTimeKeys = True
    )

    # Reset index so economy and series become regular columns
    raw = raw.reset_index()

    # Identify id columns vs year columns
    id_cols   = [c for c in raw.columns if not str(c).isdigit()]
    year_cols = [c for c in raw.columns if str(c).isdigit()]

    # Melt to long format
    df_long = raw.melt(
        id_vars    = id_cols,
        value_vars = year_cols,
        var_name   = "year",
        value_name = "value"
    )

    df_long.columns = [str(c).lower() for c in df_long.columns]
    df_long["year"] = df_long["year"].astype(int)

    # Identify the economy and series columns by name
    economy_col = "economy" if "economy" in df_long.columns else df_long.columns[0]
    series_col  = "series"  if "series"  in df_long.columns else df_long.columns[1]

    df_long = df_long.rename(columns={
        economy_col: "iso_alpha3",
        series_col:  "series"
    })

    # Map indicator codes → clean column names
    df_long["series"] = df_long["series"].map(WB_INDICATORS)
    df_long = df_long.dropna(subset=["series"])

    # Pivot: one row per (country, year), one column per indicator
    df_wide = df_long.pivot_table(
        index   = ["iso_alpha3", "year"],
        columns = "series",
        values  = "value",
        aggfunc = "first"
    ).reset_index()

    df_wide.columns.name = None

    log.info(f"  → Shape after pivot: {df_wide.shape}")
    return df_wide

# =============================================================================
# STEP C — Save raw CSVs
# =============================================================================
def save_raw_csvs(df_meta, df_macro):
    ts = datetime.now().strftime("%Y%m%d")

    meta_path  = DIRS["raw_wb"] / f"country_metadata_{ts}.csv"
    macro_path = DIRS["raw_wb"] / f"macro_economic_core_{ts}.csv"

    df_meta.to_csv(meta_path,  index=False)
    df_macro.to_csv(macro_path, index=False)

    log.info(f"  Raw metadata saved  → {meta_path}")
    log.info(f"  Raw macro saved     → {macro_path}")

# =============================================================================
# STEP D — Load into SQLite
# =============================================================================
def load_to_sqlite(df_meta, df_macro):
    log.info("Loading data into SQLite...")
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ── country_metadata ──────────────────────────────────────────────────────
    inserted_meta = 0
    skipped_meta  = 0
    for _, row in df_meta.iterrows():
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO country_metadata
                    (iso_alpha3, country_name, region, income_group)
                VALUES (?, ?, ?, ?)
            """, (
                row["iso_alpha3"],
                row["country_name"],
                row.get("region"),
                row.get("income_group"),
            ))
            if cursor.rowcount > 0:
                inserted_meta += 1
            else:
                skipped_meta += 1
        except Exception as e:
            log.warning(f"  Skipping metadata row {row['iso_alpha3']}: {e}")

    log.info(f"  country_metadata → {inserted_meta} inserted, {skipped_meta} skipped")

    # ── macro_economic_core ───────────────────────────────────────────────────
    expected_cols = [
        "iso_alpha3", "year",
        "gdp_per_capita_usd", "gdp_growth_pct", "unemployment_rate",
        "gini_index", "employment_to_pop_ratio", "trade_openness_pct_gdp",
        "gdp_per_person_employed", "govt_expenditure_pct_gdp",
        "inflation_cpi_pct", "rd_expenditure_pct_gdp",
        "labor_force_participation", "employment_share_agriculture",
        "employment_share_industry", "employment_share_services",
    ]
    for col in expected_cols:
        if col not in df_macro.columns:
            df_macro[col] = None

    df_macro = df_macro[expected_cols]

    inserted_macro = 0
    skipped_macro  = 0
    for _, row in df_macro.iterrows():
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO macro_economic_core (
                    iso_alpha3, year,
                    gdp_per_capita_usd, gdp_growth_pct, unemployment_rate,
                    gini_index, employment_to_pop_ratio, trade_openness_pct_gdp,
                    gdp_per_person_employed, govt_expenditure_pct_gdp,
                    inflation_cpi_pct, rd_expenditure_pct_gdp,
                    labor_force_participation, employment_share_agriculture,
                    employment_share_industry, employment_share_services
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, tuple(
                None if pd.isna(v) else v
                for v in row[expected_cols].values
            ))
            if cursor.rowcount > 0:
                inserted_macro += 1
            else:
                skipped_macro += 1
        except Exception as e:
            log.warning(f"  Skipping macro row {row.get('iso_alpha3')}/{row.get('year')}: {e}")

    log.info(f"  macro_economic_core → {inserted_macro} inserted, {skipped_macro} skipped")

    conn.commit()
    conn.close()

# =============================================================================
# STEP E — Verify what landed in the database
# =============================================================================
def verify_database():
    conn = sqlite3.connect(DB_PATH)

    meta_count  = pd.read_sql("SELECT COUNT(*) as n FROM country_metadata",   conn).iloc[0, 0]
    macro_count = pd.read_sql("SELECT COUNT(*) as n FROM macro_economic_core", conn).iloc[0, 0]
    year_range  = pd.read_sql(
        "SELECT MIN(year) as mn, MAX(year) as mx FROM macro_economic_core", conn
    )

    conn.close()

    log.info("\n📋 Database Verification:")
    log.info(f"   country_metadata    → {meta_count} countries")
    log.info(f"   macro_economic_core → {macro_count} rows")
    log.info(f"   Year range          → {year_range.iloc[0,0]} to {year_range.iloc[0,1]}")

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("  HISI Pipeline — World Bank Ingestion")
    log.info("=" * 60)

    df_meta  = fetch_country_metadata()
    df_macro = fetch_wb_indicators()

    save_raw_csvs(df_meta, df_macro)
    load_to_sqlite(df_meta, df_macro)
    verify_database()

    log.info("\n✅ World Bank ingestion complete.")
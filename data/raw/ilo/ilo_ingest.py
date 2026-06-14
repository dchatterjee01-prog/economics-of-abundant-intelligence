# =============================================================================
# data/raw/ilo/ilo_ingest.py  --  ILOSTAT API Data Ingestion
# =============================================================================
# ILOSTAT returns a flat list of records. Some indicators have sex/classif1
# breakdown columns; others use a simpler schema without them.
# This script handles both schemas automatically.
# =============================================================================

import sys
import io
import sqlite3
import logging
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from time import sleep

# Fix Windows cp1252 Unicode issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# -- Import config -------------------------------------------------------------
sys.path.append(str(Path(__file__).resolve().parents[3]))
from config import DB_PATH, DIRS, YEAR_START, YEAR_END, LOG_FILE

# -- Logging Setup -------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

# -- ILOSTAT API ---------------------------------------------------------------
ILO_BASE_URL = "https://rplumber.ilo.org/data/indicator/"

# Indicators with their expected schema type:
#   "simple"    -> only ref_area, time, obs_value (no sex/classif1)
#   "breakdown" -> has sex and classif1 columns needing aggregate filter
ILO_INDICATORS_UPDATED = {
    "LAP_2GDP_NOC_RT_A":     ("labor_income_share_pct",   "simple"),
    "SDG_0111_SEX_AGE_RT_A": ("working_poverty_rate",     "breakdown"),
    "UNE_2EAP_SEX_AGE_RT_A": ("youth_unemployment_rate",  "breakdown"),
    "EAP_2WAP_SEX_AGE_RT_A": ("youth_lfp_rate",           "breakdown"),
}

# Aggregate total codes for sex dimension
SEX_TOTAL_CODES = {"SEX_T", "T", "MF", "TOTAL", "_T"}

# Aggregate total codes for classif1 dimension
CLASSIF_TOTAL_CODES = {
    "AGE_AGGREGATE_TOTAL",
    "AGE_YTHADULT_YTH",
    "AGE_AGGREGATE_Y15-24",
    "ECO_SECTOR_TOTAL",
    "EDU_AGGREGATE_TOTAL",
    "OCU_SKILL_TOTAL",
    "_T", "TOTAL", "T",
}

# =============================================================================
# STEP A -- Fetch one indicator, auto-detect schema, return clean DataFrame
# =============================================================================
def fetch_ilo_indicator(
    indicator_code: str,
    clean_name: str,
    schema: str
) -> pd.DataFrame:

    log.info(f"  Fetching: {indicator_code} -> {clean_name}  [schema: {schema}]")

    params = {
        "id":          indicator_code,
        "startPeriod": str(YEAR_START),
        "endPeriod":   str(YEAR_END),
        "format":      "json",
        "lang":        "en",
    }

    try:
        response = requests.get(ILO_BASE_URL, params=params, timeout=120)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as e:
        log.warning(f"  HTTP error for {indicator_code}: {e}")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        log.warning(f"  Request error for {indicator_code}: {e}")
        return pd.DataFrame()

    if not isinstance(data, list) or len(data) == 0:
        log.warning(f"  Empty or unexpected response for {indicator_code}")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    log.info(f"  Raw columns: {list(df.columns)}")
    log.info(f"  Raw rows   : {len(df)}")

    # -- Auto-detect actual schema from columns --------------------------------
    has_sex     = "sex"     in df.columns
    has_classif = "classif1" in df.columns

    # -- Apply aggregate filters only if columns exist -------------------------
    if has_sex:
        before = len(df)
        df = df[df["sex"].isin(SEX_TOTAL_CODES)]
        log.info(f"  After sex filter    : {len(df)} rows (was {before})")

        # If sex filter wiped everything, try without it
        if len(df) == 0:
            df = pd.DataFrame(data)
            log.warning(f"  Sex filter removed all rows -- skipping sex filter")
            log.warning(f"  Unique sex values: {pd.DataFrame(data)['sex'].unique()}")

    if has_classif and len(df) > 0:
        before = len(df)
        df_filtered = df[df["classif1"].isin(CLASSIF_TOTAL_CODES)]

        if len(df_filtered) == 0:
            # Log what classif1 values actually exist
            unique_classif = df["classif1"].unique()
            log.warning(f"  classif1 filter removed all rows")
            log.warning(f"  Unique classif1 values: {unique_classif[:20]}")
            # Take the most frequent classif1 value as fallback
            top_classif = df["classif1"].value_counts().index[0]
            df_filtered = df[df["classif1"] == top_classif]
            log.warning(f"  Falling back to most common classif1: {top_classif} ({len(df_filtered)} rows)")

        df = df_filtered
        log.info(f"  After classif filter: {len(df)} rows (was {before})")

    # -- Standardise columns ---------------------------------------------------
    if "ref_area" not in df.columns or "obs_value" not in df.columns:
        log.warning(f"  Missing ref_area or obs_value for {indicator_code}")
        return pd.DataFrame()

    time_col = "time" if "time" in df.columns else None
    if time_col is None:
        log.warning(f"  No time column found for {indicator_code}")
        return pd.DataFrame()

    df = df.rename(columns={
        "ref_area":  "iso_alpha3",
        time_col:    "year",
        "obs_value": clean_name,
    })

    df["year"]     = pd.to_numeric(df["year"],     errors="coerce").astype("Int64")
    df[clean_name] = pd.to_numeric(df[clean_name], errors="coerce")

    # Filter to study years
    df = df[df["year"].between(YEAR_START, YEAR_END)]

    # One value per country-year
    df = (
        df[["iso_alpha3", "year", clean_name]]
        .dropna(subset=["iso_alpha3", "year"])
        .groupby(["iso_alpha3", "year"])[clean_name]
        .mean()
        .reset_index()
    )

    log.info(f"  -> {len(df)} clean rows for {clean_name}")
    return df

# =============================================================================
# STEP B -- Fetch all indicators and merge into one panel
# =============================================================================
def fetch_all_ilo_indicators() -> pd.DataFrame:
    log.info("Fetching all ILO indicators...")

    frames = []
    for code, (name, schema) in ILO_INDICATORS_UPDATED.items():
        df = fetch_ilo_indicator(code, name, schema)
        if not df.empty:
            frames.append(df)
        sleep(2)

    if not frames:
        log.error("No ILO data fetched at all.")
        return pd.DataFrame()

    # Outer merge all frames on iso_alpha3 + year
    df_merged = frames[0]
    for df in frames[1:]:
        df_merged = pd.merge(df_merged, df, on=["iso_alpha3", "year"], how="outer")

    df_merged = (
        df_merged[df_merged["year"].between(YEAR_START, YEAR_END)]
        .sort_values(["iso_alpha3", "year"])
        .reset_index(drop=True)
    )

    log.info(f"  -> Final merged shape : {df_merged.shape}")
    log.info(f"  -> Columns            : {list(df_merged.columns)}")
    return df_merged

# =============================================================================
# STEP C -- Save raw CSV
# =============================================================================
def save_raw_csv(df: pd.DataFrame):
    ts   = datetime.now().strftime("%Y%m%d")
    path = DIRS["raw_ilo"] / f"labor_dynamics_{ts}.csv"
    df.to_csv(path, index=False, encoding="utf-8")
    log.info(f"  Raw ILO data saved -> {path}")

# =============================================================================
# STEP D -- Load into SQLite
# =============================================================================
def load_to_sqlite(df: pd.DataFrame):
    log.info("Loading ILO data into SQLite...")

    expected_cols = [
        "iso_alpha3", "year",
        "labor_income_share_pct",
        "working_poverty_rate",
        "youth_lfp_rate",
        "youth_unemployment_rate",
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    df = df[expected_cols]

    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Clear old data so we get a clean reload
    cursor.execute("DELETE FROM labor_dynamics;")
    log.info("  Cleared existing labor_dynamics rows for clean reload")

    inserted = 0
    skipped  = 0

    for _, row in df.iterrows():
        cursor.execute(
            "SELECT 1 FROM country_metadata WHERE iso_alpha3 = ?",
            (row["iso_alpha3"],)
        )
        if cursor.fetchone() is None:
            skipped += 1
            continue

        try:
            cursor.execute("""
                INSERT OR IGNORE INTO labor_dynamics (
                    iso_alpha3, year,
                    labor_income_share_pct,
                    working_poverty_rate,
                    youth_lfp_rate,
                    youth_unemployment_rate
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                row["iso_alpha3"],
                int(row["year"]),
                None if pd.isna(row["labor_income_share_pct"])  else float(row["labor_income_share_pct"]),
                None if pd.isna(row["working_poverty_rate"])     else float(row["working_poverty_rate"]),
                None if pd.isna(row["youth_lfp_rate"])           else float(row["youth_lfp_rate"]),
                None if pd.isna(row["youth_unemployment_rate"])  else float(row["youth_unemployment_rate"]),
            ))
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            log.warning(f"  Skipping {row['iso_alpha3']}/{row['year']}: {e}")

    conn.commit()
    conn.close()
    log.info(f"  labor_dynamics -> {inserted} inserted, {skipped} skipped")

# =============================================================================
# STEP E -- Verify
# =============================================================================
def verify_database():
    conn = sqlite3.connect(DB_PATH)

    count      = pd.read_sql("SELECT COUNT(*) as n FROM labor_dynamics", conn).iloc[0, 0]
    year_range = pd.read_sql(
        "SELECT MIN(year) as mn, MAX(year) as mx FROM labor_dynamics", conn
    )
    countries  = pd.read_sql(
        "SELECT COUNT(DISTINCT iso_alpha3) as n FROM labor_dynamics", conn
    ).iloc[0, 0]

    coverage = pd.read_sql("""
        SELECT
            COUNT(labor_income_share_pct)  as has_labor_share,
            COUNT(working_poverty_rate)    as has_poverty,
            COUNT(youth_lfp_rate)          as has_youth_lfp,
            COUNT(youth_unemployment_rate) as has_youth_unemp
        FROM labor_dynamics
    """, conn)

    conn.close()

    log.info("\n--- Database Verification ---")
    log.info(f"   labor_dynamics -> {count} rows")
    log.info(f"   Countries      -> {countries} unique")
    log.info(f"   Year range     -> {year_range.iloc[0,0]} to {year_range.iloc[0,1]}")
    log.info(f"\n   Non-null counts per indicator:")
    log.info(f"   {coverage.to_string(index=False)}")

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("  HISI Pipeline -- ILO Labor Dynamics Ingestion")
    log.info("=" * 60)

    df = fetch_all_ilo_indicators()

    if not df.empty:
        save_raw_csv(df)
        load_to_sqlite(df)
        verify_database()
        log.info("\nILO ingestion complete.")
    else:
        log.error("Ingestion failed -- no data to load.")
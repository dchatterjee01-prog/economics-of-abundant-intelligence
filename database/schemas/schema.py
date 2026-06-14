# =============================================================================
# database/schemas/schema.py  —  SQLite Database Schema for HISI Pipeline
# =============================================================================
# Creates all 5 relational tables with primary keys, foreign keys, and indexes.
# Run this ONCE to initialize the database. Safe to re-run (uses IF NOT EXISTS).
# =============================================================================

import sqlite3
import sys
from pathlib import Path

# ── Import config from project root ───────────────────────────────────────────
sys.path.append(str(Path(__file__).resolve().parents[2]))
from config import DB_PATH

def create_database():

    print(f"📦 Connecting to database at:\n   {DB_PATH}\n")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign key enforcement (SQLite requires this explicitly)
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")

    # =========================================================================
    # TABLE 1: country_metadata
    # Master reference table. Every other table's iso_alpha3 + year
    # must exist here first.
    # =========================================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS country_metadata (
            iso_alpha3      TEXT        NOT NULL,
            country_name    TEXT        NOT NULL,
            region          TEXT,
            income_group    TEXT,
            PRIMARY KEY (iso_alpha3)
        );
    """)
    print("✅ Table created: country_metadata")

    # =========================================================================
    # TABLE 2: macro_economic_core
    # World Bank indicators — GDP, unemployment, Gini, trade, R&D, etc.
    # =========================================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS macro_economic_core (
            iso_alpha3                  TEXT    NOT NULL,
            year                        INTEGER NOT NULL,
            gdp_per_capita_usd          REAL,
            gdp_growth_pct              REAL,
            unemployment_rate           REAL,
            gini_index                  REAL,
            employment_to_pop_ratio     REAL,
            trade_openness_pct_gdp      REAL,
            gdp_per_person_employed     REAL,
            govt_expenditure_pct_gdp    REAL,
            inflation_cpi_pct           REAL,
            rd_expenditure_pct_gdp      REAL,
            labor_force_participation   REAL,
            employment_share_agriculture REAL,
            employment_share_industry   REAL,
            employment_share_services   REAL,
            PRIMARY KEY (iso_alpha3, year),
            FOREIGN KEY (iso_alpha3)
                REFERENCES country_metadata(iso_alpha3)
                ON DELETE CASCADE
        );
    """)
    print("✅ Table created: macro_economic_core")

    # =========================================================================
    # TABLE 3: labor_dynamics
    # ILOSTAT indicators — labor income share, working poverty, youth metrics.
    # =========================================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS labor_dynamics (
            iso_alpha3              TEXT    NOT NULL,
            year                    INTEGER NOT NULL,
            labor_income_share_pct  REAL,
            working_poverty_rate    REAL,
            youth_lfp_rate          REAL,
            youth_unemployment_rate REAL,
            PRIMARY KEY (iso_alpha3, year),
            FOREIGN KEY (iso_alpha3)
                REFERENCES country_metadata(iso_alpha3)
                ON DELETE CASCADE
        );
    """)
    print("✅ Table created: labor_dynamics")

    # =========================================================================
    # TABLE 4: ai_vibrancy_readiness
    # Stanford AI Index + Oxford Insights — AI investment, patents,
    # digital readiness, human capital scores.
    # =========================================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_vibrancy_readiness (
            iso_alpha3              TEXT    NOT NULL,
            year                    INTEGER NOT NULL,
            ai_investment_usd_mn    REAL,
            ai_patents_count        REAL,
            ai_readiness_score      REAL,
            digital_human_capital   REAL,
            govt_ai_strategy_score  REAL,
            PRIMARY KEY (iso_alpha3, year),
            FOREIGN KEY (iso_alpha3)
                REFERENCES country_metadata(iso_alpha3)
                ON DELETE CASCADE
        );
    """)
    print("✅ Table created: ai_vibrancy_readiness")

    # =========================================================================
    # TABLE 5: institutional_buffers
    # IMF-sourced — social spending, fiscal space, safety net coverage.
    # =========================================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS institutional_buffers (
            iso_alpha3                  TEXT    NOT NULL,
            year                        INTEGER NOT NULL,
            social_protection_spending  REAL,
            health_expenditure_pct_gdp  REAL,
            education_expenditure_pct_gdp REAL,
            fiscal_balance_pct_gdp      REAL,
            social_safety_net_coverage  REAL,
            PRIMARY KEY (iso_alpha3, year),
            FOREIGN KEY (iso_alpha3)
                REFERENCES country_metadata(iso_alpha3)
                ON DELETE CASCADE
        );
    """)
    print("✅ Table created: institutional_buffers")

    # =========================================================================
    # INDEXES — Speeds up JOIN and WHERE operations across the panel
    # =========================================================================
    indexes = [
        ("idx_macro_year",    "macro_economic_core",   "year"),
        ("idx_macro_iso",     "macro_economic_core",   "iso_alpha3"),
        ("idx_labor_year",    "labor_dynamics",        "year"),
        ("idx_labor_iso",     "labor_dynamics",        "iso_alpha3"),
        ("idx_ai_year",       "ai_vibrancy_readiness", "year"),
        ("idx_ai_iso",        "ai_vibrancy_readiness", "iso_alpha3"),
        ("idx_buffer_year",   "institutional_buffers", "year"),
        ("idx_buffer_iso",    "institutional_buffers", "iso_alpha3"),
    ]

    for idx_name, table, column in indexes:
        cursor.execute(f"""
            CREATE INDEX IF NOT EXISTS {idx_name}
            ON {table}({column});
        """)
    print("✅ All indexes created")

    # =========================================================================
    # Verify — List all tables created
    # =========================================================================
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()

    print("\n📋 Tables confirmed in database:")
    for t in tables:
        print(f"   → {t[0]}")

    conn.commit()
    conn.close()
    print("\n🎉 Database initialized successfully.")
    print(f"   File saved at: {DB_PATH}")

if __name__ == "__main__":
    create_database()
# sql_diagnostic.py -- Extract SQL schema and query examples for README
import sys, io, sqlite3, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.append(".")
from config import DB_PATH

conn = sqlite3.connect(DB_PATH)

print("=" * 70)
print("  SQL DIAGNOSTIC FOR README")
print("=" * 70)

# 1. Table schemas
print("\n[1] TABLE SCHEMAS")
print("-" * 50)
tables = ["country_metadata", "macro_economic_core", "labor_dynamics",
          "ai_vibrancy_readiness", "institutional_buffers"]
for t in tables:
    print(f"\n-- {t}")
    schema = pd.read_sql(f"PRAGMA table_info({t})", conn)
    print(schema[["name", "type", "pk"]].to_string(index=False))

# 2. Check if panel_features and hisi_panel tables exist
print("\n[2] ADDITIONAL TABLES")
print("-" * 50)
all_tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", conn
)
print(all_tables.to_string(index=False))

# 3. Sample CTE-style query -- top HISI countries by region in 2022
print("\n[3] SAMPLE QUERY -- TOP HISI BY REGION 2022")
print("-" * 50)
try:
    q = """
    SELECT
        cm.region,
        cm.iso_alpha3,
        cm.country_name,
        hp.hisi_score,
        hp.cluster_label,
        ROW_NUMBER() OVER (
            PARTITION BY cm.region
            ORDER BY hp.hisi_score DESC
        ) as rank_in_region
    FROM hisi_panel hp
    JOIN country_metadata cm ON hp.iso_alpha3 = cm.iso_alpha3
    WHERE hp.year = 2022
    QUALIFY rank_in_region <= 2
    ORDER BY cm.region, rank_in_region
    """
    # SQLite doesn't support QUALIFY -- use subquery
    q2 = """
    SELECT * FROM (
        SELECT
            cm.region,
            cm.iso_alpha3,
            cm.country_name,
            hp.hisi_score,
            hp.cluster_label,
            ROW_NUMBER() OVER (
                PARTITION BY cm.region
                ORDER BY hp.hisi_score DESC
            ) as rank_in_region
        FROM hisi_panel hp
        JOIN country_metadata cm ON hp.iso_alpha3 = cm.iso_alpha3
        WHERE hp.year = 2022
    ) ranked
    WHERE rank_in_region <= 2
    ORDER BY region, rank_in_region
    """
    df = pd.read_sql(q2, conn)
    print(df.to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

# 4. Sample Window Function -- rolling avg HISI per country
print("\n[4] SAMPLE QUERY -- ROLLING AVG HISI (WINDOW FUNCTION)")
print("-" * 50)
try:
    q = """
    SELECT
        iso_alpha3,
        year,
        hisi_score,
        AVG(hisi_score) OVER (
            PARTITION BY iso_alpha3
            ORDER BY year
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ) as hisi_rolling_avg_3yr,
        hisi_score - LAG(hisi_score, 1) OVER (
            PARTITION BY iso_alpha3 ORDER BY year
        ) as hisi_yoy_change
    FROM hisi_panel
    WHERE iso_alpha3 IN ('USA', 'IND', 'NGA', 'DEU', 'BRA')
    AND year >= 2018
    ORDER BY iso_alpha3, year
    """
    df = pd.read_sql(q, conn)
    print(df.to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

# 5. Sample CTE -- AI exposure vs HISI by income group
print("\n[5] SAMPLE QUERY -- CTE: AI EXPOSURE vs HISI BY INCOME GROUP")
print("-" * 50)
try:
    q = """
    WITH exposure_summary AS (
        SELECT
            cm.income_group,
            AVG(pf.ai_exposure_proxy)    as avg_ai_exposure,
            AVG(hp.hisi_score)           as avg_hisi,
            AVG(mc.gini_index)           as avg_gini,
            COUNT(DISTINCT pf.iso_alpha3) as n_countries
        FROM panel_features pf
        JOIN country_metadata cm  ON pf.iso_alpha3 = cm.iso_alpha3
        JOIN hisi_panel hp        ON pf.iso_alpha3 = hp.iso_alpha3
                                 AND pf.year = hp.year
        JOIN macro_economic_core mc ON pf.iso_alpha3 = mc.iso_alpha3
                                   AND pf.year = mc.year
        WHERE pf.year BETWEEN 2015 AND 2022
          AND cm.income_group IS NOT NULL
        GROUP BY cm.income_group
    )
    SELECT
        income_group,
        ROUND(avg_ai_exposure, 2)  as avg_ai_exposure,
        ROUND(avg_hisi, 2)         as avg_hisi_score,
        ROUND(avg_gini, 2)         as avg_gini,
        n_countries
    FROM exposure_summary
    ORDER BY avg_hisi_score DESC
    """
    df = pd.read_sql(q, conn)
    print(df.to_string(index=False))
except Exception as e:
    print(f"  Error: {e}")

conn.close()
print("\n" + "=" * 70)
print("  SQL DIAGNOSTIC COMPLETE")
print("=" * 70)
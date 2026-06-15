# The Economics of Abundant Intelligence
## Who Wins, Who Falls, and Who Adapts?
### Global Evidence on Income Stability and Career Sustainability in the AI Era

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/SQLite-Database-lightgrey?style=for-the-badge&logo=sqlite" />
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit" />
  <img src="https://img.shields.io/badge/XGBoost-Forecasting-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Panel-6774%20obs-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Countries-264-blueviolet?style=for-the-badge" />
</p>

<p align="center">
  <b>Daipayan Chatterjee</b><br>
  M.Sc. Economics | Specialization: Quantitative Economics &amp; Econometrics<br>
</p>

<p align="center">
  <a href="https://economics-of-abundant-intelligence-daipayan-chatterjee.streamlit.app/">
    <img src="https://img.shields.io/badge/Live%20Dashboard-Launch%20App-FF4B4B?style=for-the-badge&logo=streamlit" />
  </a>
  &nbsp;
  <a href="Economics_of_Abundant_Intelligence_Daipayan_Chatterjee.pptx">
    <img src="https://img.shields.io/badge/Presentation-Download%20PPT-B7472A?style=for-the-badge&logo=microsoft-powerpoint" />
  </a>
</p>

<p align="center">
  <a href="#research-overview">Overview</a> &bull;
  <a href="#research-hypotheses">Hypotheses</a> &bull;
  <a href="#methodology">Methodology</a> &bull;
  <a href="#key-findings">Key Findings</a> &bull;
  <a href="#hisi-index">HISI Index</a> &bull;
  <a href="#forecasts-to-2050">2050 Forecasts</a> &bull;
  <a href="#reproducing-results">Reproduce</a>
</p>

---

## Table of Contents

- [Research Overview](#research-overview)
- [Research Hypotheses](#research-hypotheses)
- [Data Architecture](#data-architecture)
- [Methodology](#methodology)
- [Key Findings](#key-findings)
- [HISI Index](#hisi-index)
- [Cluster Analysis](#cluster-analysis)
- [Forecasts to 2050](#forecasts-to-2050)
- [Pipeline Architecture](#pipeline-architecture)
- [Reproducing Results](#reproducing-results)
- [Technical Stack](#technical-stack)
- [Policy Implications](#economic-interpretation--policy-implications)
- [SQL Engineering](#sql-engineering)
- [Citation](#citation)

---

## Research Overview

The rapid diffusion of artificial intelligence technologies is reshaping global labor markets at a speed and scale unprecedented in modern economic history. Yet the distributional consequences of this transformation remain deeply unresolved — who captures the gains, who absorbs the displacement, and which institutional architectures determine the difference?

This project constructs an end-to-end, production-grade quantitative research pipeline analyzing **264 countries across 26 years (2000–2025)** — totaling **6,774 country-year observations** — to systematically answer these questions.

The centerpiece is the **Human Income Stability Index (HISI)**: a novel, mathematically grounded composite metric that captures a country's ability to maintain equitable income distribution in the face of AI-driven structural transformation.

**Core research question:** Does AI exposure systematically destabilize labor income shares and amplify labor market stress — and do institutional buffers meaningfully moderate this relationship?

---

## Research Hypotheses

| # | Hypothesis | Direction | Status |
|---|---|---|---|
| H1 | AI exposure increases labor market stress | Positive | Supported (p < 0.10) |
| H2 | Strong social buffers protect labor income share | Positive | **Strongly supported** (p < 0.001) |
| H3 | Economic resilience reduces unemployment | Negative | **Strongly supported** (p < 0.001) |
| H4 | Higher inequality amplifies labor market stress | Positive | **Strongly supported** (p < 0.001) |
| H5 | Human capital buffers unemployment | Negative | Supported (p < 0.10) |
| H6 | Fixed effects dominate random effects specification | — | **Confirmed** (Hausman p = 0.000 across all models) |

---

## Data Architecture

This pipeline bypasses flat CSV joins entirely, implementing a **normalized relational SQLite database** with 5 structured tables, proper primary keys, foreign keys, and indexes.

```
hisi_panel.db  (8.83 MB)
│
├── country_metadata          266 rows  |  4 cols   [World Bank economy list]
├── macro_economic_core      6759 rows  | 16 cols   [World Bank WDI API]
├── labor_dynamics           4822 rows  |  6 cols   [ILOSTAT REST API]
├── ai_vibrancy_readiness    1820 rows  |  7 cols   [Oxford Insights + Stanford AI Index]
└── institutional_buffers    5933 rows  |  7 cols   [World Bank WDI Social Spending]
```

### Data Sources

| Source | Indicators | Coverage |
|---|---|---|
| World Bank WDI API | GDP per capita, Gini index, unemployment, trade openness, R&D expenditure, employment shares | 263 countries, 2000–2025 |
| ILOSTAT REST API | Labor income share, working poverty rate, youth unemployment, youth LFP | 186 countries, 2000–2025 |
| Oxford Insights Government AI Readiness Index | AI readiness score, digital human capital, government AI strategy | 70 countries, anchored 2022 |
| World Bank WDI Social Spending | Health expenditure, education expenditure, fiscal balance | 253 countries, 2000–2025 |

### World Bank Indicator Codes

```python
WB_INDICATORS = {
    "NY.GDP.PCAP.CD":    "gdp_per_capita_usd",
    "NY.GDP.MKTP.KD.ZG": "gdp_growth_pct",
    "SL.UEM.TOTL.ZS":    "unemployment_rate",
    "SI.POV.GINI":        "gini_index",
    "NE.TRD.GNFS.ZS":    "trade_openness_pct_gdp",
    "GC.XPN.TOTL.GD.ZS": "govt_expenditure_pct_gdp",
    "GB.XPD.RSDV.GD.ZS": "rd_expenditure_pct_gdp",
    "SL.TLF.CACT.ZS":    "labor_force_participation",
    "SL.AGR.EMPL.ZS":    "employment_share_agriculture",
    "SL.IND.EMPL.ZS":    "employment_share_industry",
    "SL.SRV.EMPL.ZS":    "employment_share_services",
}
```

---

## Methodology

### 1. Imputation Strategy

Real-world macro panel data is structurally incomplete. We implement a three-stage localized imputation cascade — never dropping rows, never using primitive global mean-filling:

**Stage 1:** Localized rolling forward-fill then backward-fill within each country group (window = 3 years)

**Stage 2:** KNN Imputer (k = 5) for structural missingness, preserving cross-sectional relationships

**Stage 3:** Drop columns exceeding 60% missingness threshold globally

Final imputed panel: **6,774 observations × 31 variables**

---

### 2. Feature Engineering

**AI Exposure Proxy** — interaction of AI readiness and services employment:

$$\text{AI Exposure}_{i,t} = \text{AI Readiness Score}_{i,t} \times \text{Employment Share Services}_{i,t}$$

**Tech Vulnerability Index** — captures structural displacement risk without institutional cushioning:

$$\text{TVI}_{i,t} = \text{AI Exposure}_{i,t} \times \left(1 - \frac{\text{Social Buffer}_{i,t}}{100}\right)$$

**Social Buffer Index** — composite institutional protection score:

$$\text{SBI}_{i,t} = \frac{1}{3}\left(\text{Health Exp}_{i,t} + \text{Education Exp}_{i,t} + \text{Govt Exp}_{i,t}\right)_{\text{Norm}}$$

Total engineered features: **82 variables** including rolling means (MA3), one-year and three-year lags, regional interaction terms, and income group dummies.

---

### 3. Two-Way Fixed Effects Panel Regression

The core econometric specification absorbs both unobserved country-level heterogeneity (geography, historical institutions) and global time shocks (financial crises, pandemic, frontier AI breakthroughs):

$$Y_{i,t} = \beta_0 + \beta_1 \left(\text{AI Exposure}_{i,t}\right) + \beta_2 \left(\text{Tech Vulnerability}_{i,t}\right) + \gamma \mathbf{X}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}$$

Where:
- $Y_{i,t}$ is one of: Labor Income Share, Unemployment Rate, or Labor Market Stress
- $\alpha_i$ = country fixed effects capturing time-invariant unobservables
- $\delta_t$ = year fixed effects capturing global macro shocks
- $\mathbf{X}_{i,t}$ = vector of time-varying controls: Gini index, GDP growth, trade openness, government expenditure, human capital index, economic resilience
- Standard errors clustered at the country level to control for serial correlation and heteroskedasticity

**Estimated using:** `linearmodels.PanelOLS` with entity and time effects

---

### 4. Endogeneity and Robustness

Wealthy countries adopt AI faster — creating reverse causality bias in naive OLS. We address this rigorously:

**Hausman Test** — formally confirms fixed effects dominate random effects:

| Dependent Variable | FE R² Within | RE R² | Hausman Stat | p-value | Verdict |
|---|---|---|---|---|---|
| Labor Income Share | 0.0704 | 0.4775 | 69.31 | 0.000 | **Use Fixed Effects** |
| Unemployment Rate | 0.0833 | 0.1163 | 69.22 | 0.000 | **Use Fixed Effects** |
| Labor Market Stress | 0.2136 | 0.2026 | 82.57 | 0.000 | **Use Fixed Effects** |

**IV2SLS Robustness** — Instrumental Variables using lagged regressors as instruments, confirming TWFE directional consistency across all specifications.

**Regional Robustness** — TWFE re-estimated across 7 World Bank regions, confirming South Asia significance and North America marginal significance.

---

## Key Findings

### Finding 1 — Social Buffers Are the Primary Stabilizer of Labor Income

$$\hat{\beta}_{\text{Social Buffer}} = +0.264 \quad (p < 0.001, \quad R^2_{\text{within}} = 0.0449)$$

A one-unit increase in the Social Buffer Index raises labor income share by **0.264 percentage points**, net of country and year fixed effects. This is the single strongest significant predictor in the labor income share model — stronger than AI exposure, GDP growth, or trade openness.

---

### Finding 2 — Economic Resilience Is the Most Powerful Unemployment Buffer

$$\hat{\beta}_{\text{Economic Resilience}} = -2.950 \quad (p < 0.001)$$

$$\hat{\beta}_{\text{Govt Expenditure}} = +0.033 \quad (p < 0.001)$$

Economic resilience exerts the largest magnitude effect in the unemployment model. Notably, government expenditure **increases** unemployment at the margin — consistent with a Wagner's Law crowding-out effect observable in advanced economies.

---

### Finding 3 — AI Exposure Increases Labor Market Stress

$$\hat{\beta}_{\text{AI Exposure}} = +0.143 \quad (p = 0.084)$$

AI exposure exerts a positive, marginally significant pressure on labor market stress — consistent with task displacement theory. Critically, the Tech Vulnerability Index **significantly moderates** this stress:

$$\hat{\beta}_{\text{Tech Vulnerability}} = -0.214 \quad (p = 0.043)$$

The sign difference reveals a **moderation effect**: countries with high AI exposure but strong institutional buffers experience significantly lower net labor market stress than those without protection.

---

### Finding 4 — Inequality Directly Amplifies Labor Market Stress

$$\hat{\beta}_{\text{Gini}} = +0.100 \quad (p < 0.001)$$

Higher pre-existing inequality makes labor markets structurally more fragile under AI pressure — a vicious cycle where unequal economies are least equipped to absorb automation shocks.

---

### Finding 5 — IV2SLS Confirms Social Buffer Causality

After instrumenting for endogeneity using lagged regressors:

$$\hat{\beta}_{\text{Social Buffer}}^{\text{IV}} = +0.288 \quad (p = 0.010)$$

The IV estimate is **larger** than the TWFE estimate (+0.264), confirming the TWFE coefficient is a conservative lower bound. The true causal effect of social protection on labor income stability is at least as large as the panel estimate suggests.

---

### Finding 6 — Top XGBoost Predictors Confirm Econometric Findings

| Rank | Feature | Importance |
|---|---|---|
| 1 | Labor Income Share | 30.6% |
| 2 | Labor Income Share (MA3) | 18.1% |
| 3 | Gini Index | 11.9% |
| 4 | Gini Index Lag 1 | 7.3% |
| 5 | AI Exposure × ECS Region | 5.8% |
| 6 | Region: Europe and Central Asia | 4.3% |
| 7 | Social Buffer Index | 2.8% |

Labor income share and the Gini index together account for **nearly 50%** of XGBoost predictive power — confirming their centrality in the HISI construction.

---

## HISI Index

### Mathematical Formulation

The **Human Income Stability Index (HISI)** is a novel composite metric capturing a country's ability to maintain equitable income distribution under AI-driven structural transformation:

$$\text{HISI}_{i,t} = w_1 \cdot \left(\frac{\text{Labor Share}_{i,t}}{\text{Gini}_{i,t}}\right)_{\text{Norm}} + w_2 \cdot \left(\text{Social Protection}_{i,t}\right)_{\text{Norm}} - w_3 \cdot \left(\text{AI Displacement Risk}_{i,t}\right)_{\text{Norm}}$$

**Weights determined via Principal Component Analysis (PCA):**

| Component | Weight | Interpretation |
|---|---|---|
| $w_1$ — Labor Equity Ratio | 0.40 | Labor share relative to inequality |
| $w_2$ — Social Protection Score | 0.35 | Institutional safety net strength |
| $w_3$ — AI Displacement Risk | 0.25 | Structural automation exposure (subtracted) |

**HISI scale:** 0 (maximum instability) to 100 (maximum stability)

### HISI Score Range: 19.45 to 88.52

| Rank | Country | Avg HISI 2000–2025 | Cluster |
|---|---|---|---|
| 1 | Iceland | 88.52 | The Wins |
| 2 | Slovenia | 88.12 | The Wins |
| 3 | Belgium | 85.32 | The Wins |
| 4 | Denmark | 82.79 | The Wins |
| 5 | Netherlands | 78.88 | The Wins |
| 6 | Finland | 75.58 | The Wins |
| 7 | Sweden | 75.36 | The Wins |
| 8 | Austria | 75.01 | The Wins |
| ... | ... | ... | ... |
| 261 | Tajikistan | 23.30 | The Falls |
| 262 | Mexico | 23.20 | The Adapters |
| 263 | Venezuela | 21.47 | The Adapters |
| 264 | Qatar | 19.45 | The Adapters |

---

## Cluster Analysis

Countries are segmented dynamically using **Gaussian Mixture Models (GMM)** on HISI component scores into three structurally distinct groups:

### The Wins
*High Digital Capital · Stable HISI · Strong Institutional Buffers*

Nordic economies, Western Europe, Australia, Canada. These countries combine strong labor protections, high social spending, and managed AI adoption curves. Iceland, Slovenia, Belgium, Denmark, and the Netherlands lead this group.

### The Falls
*High Task Displacement Risk · Weak Institutional Buffers*

Sub-Saharan Africa, parts of Southeast Asia, fragile states. Characterized by high informal employment exposure, thin social safety nets, and low AI governance readiness. Most vulnerable to uncushioned automation shocks.

### The Adapters
*High AI Exposure · Emerging but Incomplete Institutional Responses*

A heterogeneous group including emerging markets with growing digital sectors but lagging social infrastructure. India, Czech Republic, and Moldova appear here — high AI exposure but building institutional responses. The critical policy battleground of the coming decade.

---

## Forecasts to 2050

XGBoost trained on 2000–2022 data with **expanding-window cross-validation** (CV R² = 0.990, RMSE = 1.47) forecasts HISI trajectories under two structural scenarios:

**Scenario A — Aggressive Automation:** Accelerated AI adoption (+5%/yr) with stagnating social protection (−2%/yr) and flat R&D.

**Scenario B — Equitable Adaptation:** Balanced AI scaling (+3%/yr) paired with growing social protection (+3%/yr) and rising R&D (+1%/yr).

| Horizon | Aggressive Automation | Equitable Adaptation | Policy Gap |
|---|---|---|---|
| 2030 | 44.39 | 45.71 | +1.32 |
| 2050 | 42.63 | 48.54 | **+5.90** |

**The divergence widens dramatically over time.** By 2050, the policy choice between aggressive automation and equitable adaptation creates a **5.9-point HISI gap** globally. This gap is not technological — it is entirely institutional.

---

## Pipeline Architecture

```
economics-of-abundant-intelligence/
│
├── config.py                           # Central config: paths, API codes, constants
├── verify_project.py                   # Full project file verification (100% green)
│
├── data/
│   ├── raw/
│   │   ├── world_bank/wb_ingest.py     # World Bank WDI API ingestion (wbgapi)
│   │   ├── ilo/ilo_ingest.py           # ILOSTAT REST API ingestion
│   │   └── stanford_ai/ai_ingest.py    # AI Vibrancy + Institutional Buffers
│   ├── imputed/
│   │   └── impute.py                   # 3-stage imputation: rolling + KNN + threshold
│   └── features/
│       └── build_features.py           # 82-feature engineering pipeline
│
├── database/
│   └── hisi_panel.db                   # Production database (8.83 MB, 7 tables)
│
├── models/
│   ├── panel_econometrics.py           # TWFE + cluster-robust SE (linearmodels)
│   ├── gmm_robustness.py               # IV2SLS endogeneity robustness
│   ├── hisi_construction.py            # PCA weights + HISI computation + GMM clustering
│   ├── forecasting.py                  # XGBoost + expanding-window CV + scenarios
│   ├── results/                        # All regression tables, cluster CSVs, forecasts
│   └── saved/xgb_hisi.json             # Serialized XGBoost model (2.99 MB)
│
├── dashboard/
│   └── app.py                          # Streamlit 4-page intelligence dashboard
│
├── js-powerpoint/
│   └── Economics_of_Abundant_Intelligence_Daipayan_Chatterjee.pptx
│
└── notebooks/
    └── phase1_verify.py                # Phase 1 data pipeline verification (13/13 passed)
```

---

## Reproducing Results

### 1. Clone the repository

```bash
git clone https://github.com/dchatterjee01-prog/economics-of-abundant-intelligence.git
cd economics-of-abundant-intelligence
```

### 2. Create and activate the environment

```bash
conda create -n hisi_env python=3.10 -y
conda activate hisi_env
pip install pandas numpy scipy sqlalchemy wbgapi statsmodels linearmodels scikit-learn xgboost streamlit plotly seaborn matplotlib
```

### 3. Run the full ingestion pipeline

```bash
python data/raw/world_bank/wb_ingest.py
python data/raw/ilo/ilo_ingest.py
python data/raw/stanford_ai/ai_ingest.py
```

### 4. Impute and build features

```bash
python data/imputed/impute.py
python data/features/build_features.py
```

### 5. Run econometric models and construct HISI

```bash
python models/panel_econometrics.py
python models/gmm_robustness.py
python models/hisi_construction.py
python models/forecasting.py
```

### 6. Launch the dashboard locally

```bash
streamlit run dashboard/app.py
```

Open `http://localhost:8501` in your browser.

### 7. Verify all files

```bash
python verify_project.py
```

All 20+ checks should return `[  OK  ]`.

---

## Technical Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| Environment | Anaconda, VS Code, Windows 11 |
| Database | SQLite via SQLAlchemy 2.0 |
| Data APIs | wbgapi (World Bank), ILOSTAT REST |
| Panel Econometrics | linearmodels (TWFE, IV2SLS), statsmodels |
| Imputation | scikit-learn KNNImputer + pandas rolling |
| Machine Learning | XGBoost 2.0 (rolling expanding-window CV) |
| Dimensionality Reduction | scikit-learn PCA |
| Clustering | scikit-learn GaussianMixture |
| Dashboard | Streamlit + Plotly |
| Version Control | Git + GitHub |

---

## Economic Interpretation & Policy Implications

**1. Social protection is not a luxury — it is a structural stabilizer.**
The IV2SLS estimate confirms that social buffer institutions causally protect labor income share even after controlling for reverse causality. Countries dismantling safety nets under fiscal austerity are compounding their AI vulnerability.

**2. Inequality is a force multiplier for automation risk.**
The Gini coefficient is the third most important XGBoost predictor (11.9% importance) and strongly significant in TWFE. Unequal societies are structurally less resilient to AI-driven disruption — creating a risk spiral where inequality feeds instability feeds more inequality.

**3. The 2050 divergence is a policy choice, not a technological inevitability.**
The 5.9-point HISI gap between scenarios by 2050 is driven entirely by the presence or absence of institutional responses — not by technological trajectories. The economics of abundant intelligence has a clear prescription: invest in the buffers.

**4. South Asia is the highest-risk significant region.**
Regional robustness analysis identifies South Asia as the only region where AI exposure is statistically significant at the 5% level. This warrants deeper investigation into the heterogeneous within-region effects across India, Bangladesh, and Pakistan.

---

## SQL Engineering

This project implements a **production-grade relational database** — bypassing flat CSV joins entirely. All analysis flows through a normalized SQLite schema with proper primary keys, foreign keys, indexes, and views. Queries use **Common Table Expressions (CTEs)** and **Window Functions** for readable, modular, high-performance data transformations.

### Relational Schema

```sql
-- TABLE 1: Master reference
CREATE TABLE country_metadata (
    iso_alpha3    TEXT  NOT NULL,
    country_name  TEXT  NOT NULL,
    region        TEXT,
    income_group  TEXT,
    PRIMARY KEY (iso_alpha3)
);

-- TABLE 2: World Bank macroeconomic indicators
CREATE TABLE macro_economic_core (
    iso_alpha3                   TEXT     NOT NULL,
    year                         INTEGER  NOT NULL,
    gdp_per_capita_usd           REAL,
    gdp_growth_pct               REAL,
    unemployment_rate            REAL,
    gini_index                   REAL,
    employment_to_pop_ratio      REAL,
    trade_openness_pct_gdp       REAL,
    gdp_per_person_employed      REAL,
    govt_expenditure_pct_gdp     REAL,
    inflation_cpi_pct            REAL,
    rd_expenditure_pct_gdp       REAL,
    labor_force_participation    REAL,
    employment_share_agriculture REAL,
    employment_share_industry    REAL,
    employment_share_services    REAL,
    PRIMARY KEY (iso_alpha3, year),
    FOREIGN KEY (iso_alpha3) REFERENCES country_metadata(iso_alpha3) ON DELETE CASCADE
);

-- TABLE 3: ILOSTAT labor dynamics
CREATE TABLE labor_dynamics (
    iso_alpha3               TEXT     NOT NULL,
    year                     INTEGER  NOT NULL,
    labor_income_share_pct   REAL,
    working_poverty_rate     REAL,
    youth_lfp_rate           REAL,
    youth_unemployment_rate  REAL,
    PRIMARY KEY (iso_alpha3, year),
    FOREIGN KEY (iso_alpha3) REFERENCES country_metadata(iso_alpha3) ON DELETE CASCADE
);

-- TABLE 4: Oxford Insights + Stanford AI Index
CREATE TABLE ai_vibrancy_readiness (
    iso_alpha3              TEXT     NOT NULL,
    year                    INTEGER  NOT NULL,
    ai_investment_usd_mn    REAL,
    ai_patents_count        REAL,
    ai_readiness_score      REAL,
    digital_human_capital   REAL,
    govt_ai_strategy_score  REAL,
    PRIMARY KEY (iso_alpha3, year),
    FOREIGN KEY (iso_alpha3) REFERENCES country_metadata(iso_alpha3) ON DELETE CASCADE
);

-- TABLE 5: IMF + World Bank social spending
CREATE TABLE institutional_buffers (
    iso_alpha3                     TEXT     NOT NULL,
    year                           INTEGER  NOT NULL,
    social_protection_spending     REAL,
    health_expenditure_pct_gdp     REAL,
    education_expenditure_pct_gdp  REAL,
    fiscal_balance_pct_gdp         REAL,
    social_safety_net_coverage     REAL,
    PRIMARY KEY (iso_alpha3, year),
    FOREIGN KEY (iso_alpha3) REFERENCES country_metadata(iso_alpha3) ON DELETE CASCADE
);

-- PERFORMANCE INDEXES
CREATE INDEX idx_macro_year  ON macro_economic_core(year);
CREATE INDEX idx_macro_iso   ON macro_economic_core(iso_alpha3);
CREATE INDEX idx_labor_year  ON labor_dynamics(year);
CREATE INDEX idx_ai_year     ON ai_vibrancy_readiness(year);
CREATE INDEX idx_buffer_year ON institutional_buffers(year);
```

---

### Query 1 — CTE: AI Exposure vs HISI by Income Group

```sql
WITH exposure_summary AS (
    SELECT
        cm.income_group,
        AVG(pf.ai_exposure_proxy)     AS avg_ai_exposure,
        AVG(hp.hisi_score)            AS avg_hisi,
        AVG(mc.gini_index)            AS avg_gini,
        COUNT(DISTINCT pf.iso_alpha3) AS n_countries
    FROM panel_features pf
    JOIN country_metadata    cm ON pf.iso_alpha3 = cm.iso_alpha3
    JOIN hisi_panel          hp ON pf.iso_alpha3 = hp.iso_alpha3
                               AND pf.year       = hp.year
    JOIN macro_economic_core mc ON pf.iso_alpha3 = mc.iso_alpha3
                               AND pf.year       = mc.year
    WHERE pf.year BETWEEN 2015 AND 2022
      AND cm.income_group IS NOT NULL
    GROUP BY cm.income_group
)
SELECT
    income_group,
    ROUND(avg_ai_exposure, 2) AS avg_ai_exposure,
    ROUND(avg_hisi, 2)        AS avg_hisi_score,
    ROUND(avg_gini, 2)        AS avg_gini,
    n_countries
FROM exposure_summary
ORDER BY avg_hisi_score DESC;
```

**Result:**

| Income Group | Avg AI Exposure | Avg HISI Score | Avg Gini | Countries |
|---|---|---|---|---|
| HIC (High Income) | 47.74 | 54.15 | 33.00 | 84 |
| UMC (Upper Middle) | 30.36 | 45.95 | 38.04 | 54 |
| LMC (Lower Middle) | 20.39 | 44.75 | 37.83 | 50 |
| LIC (Low Income) | 10.95 | 37.49 | 39.32 | 25 |

**Interpretation:** High-income countries have 4.4x the AI exposure of low-income countries yet score 44% higher on HISI. The Gini gradient runs in the opposite direction — confirming that AI and inequality diverge systematically across income groups.

---

### Query 2 — Window Functions: Rolling HISI and Year-on-Year Change

```sql
SELECT
    iso_alpha3,
    year,
    hisi_score,
    AVG(hisi_score) OVER (
        PARTITION BY iso_alpha3
        ORDER BY year
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )                                                    AS hisi_rolling_avg_3yr,
    hisi_score - LAG(hisi_score, 1) OVER (
        PARTITION BY iso_alpha3 ORDER BY year
    )                                                    AS hisi_yoy_change
FROM hisi_panel
WHERE iso_alpha3 IN ('USA', 'IND', 'NGA', 'DEU', 'BRA')
  AND year >= 2020
ORDER BY iso_alpha3, year;
```

**Result (2022):**

| Country | Year | HISI Score | Rolling Avg 3yr | YoY Change |
|---|---|---|---|---|
| Brazil | 2022 | 42.32 | 42.51 | +1.60 |
| Germany | 2022 | 69.86 | 72.57 | −2.12 |
| India | 2022 | 87.19 | 87.80 | −0.86 |
| Nigeria | 2022 | 74.35 | 72.94 | +1.52 |
| USA | 2022 | 54.64 | 59.03 | **−5.38** |

**Interpretation:** The United States shows a sharp HISI decline of 5.38 points in 2022 — the largest single-year drop among major economies. Germany also declines. India and Nigeria show positive trajectories.

---

### Query 3 — Window Function: Top HISI Country per Region (2022)

```sql
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
        ) AS rank_in_region
    FROM hisi_panel hp
    JOIN country_metadata cm ON hp.iso_alpha3 = cm.iso_alpha3
    WHERE hp.year = 2022
) ranked
WHERE rank_in_region <= 2
ORDER BY region, rank_in_region;
```

**Result:**

| Region | Country | HISI Score | Cluster | Rank |
|---|---|---|---|---|
| EAS | Tuvalu | 75.04 | The Wins | 1 |
| ECS | Moldova | 93.43 | The Adapters | 1 |
| ECS | Slovenia | 92.63 | The Wins | 2 |
| LCN | Puerto Rico | 63.18 | The Adapters | 1 |
| MEA | Afghanistan | 60.98 | The Wins | 1 |
| NAC | Canada | 69.38 | The Wins | 1 |
| NAC | United States | 54.64 | The Wins | 2 |
| SAS | India | 87.19 | The Adapters | 1 |
| SSF | Nigeria | 74.35 | The Falls | 1 |

---

### Database at a Glance

| Table | Rows | Countries | Primary Key |
|---|---|---|---|
| country_metadata | 266 | 266 | iso_alpha3 |
| macro_economic_core | 6,759 | 263 | iso_alpha3 + year |
| labor_dynamics | 4,822 | 186 | iso_alpha3 + year |
| ai_vibrancy_readiness | 1,820 | 70 | iso_alpha3 + year |
| institutional_buffers | 5,933 | 253 | iso_alpha3 + year |
| panel_features | 6,774 | 264 | iso_alpha3 + year |
| hisi_panel | 6,774 | 264 | iso_alpha3 + year |

---

## Citation

If you use this data pipeline, econometric framework, or simulation platform in an academic or professional capacity, please cite it using the following BibTeX entry:

```bibtex
@misc{chatterjee2026hisi,
  author = {Chatterjee, Daipayan},
  title  = {The Economics of Abundant Intelligence: Who Wins, Who Falls, and Who Adapts? Global Evidence on Income Stability and Career Sustainability in the AI Era},
  year   = {2026},
  note   = {M.Sc. Economics Research Project, West Bengal State University},
  url    = {[https://economics-of-abundant-intelligence-daipayan-chatterjee.streamlit.app/](https://economics-of-abundant-intelligence-daipayan-chatterjee.streamlit.app/)}
}

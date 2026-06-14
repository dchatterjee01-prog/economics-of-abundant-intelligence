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
  M.Sc. Economics | Specialization: Quantitative Economics & Econometrics<br>
  <a href="https://economics-of-abundant-intelligence.streamlit.app">🚀 Live Dashboard</a> •
  <a href="#methodology">Methodology</a> •
  <a href="#key-findings">Key Findings</a> •
  <a href="#hisi-index">HISI Index</a> •
  <a href="#forecasts">2050 Forecasts</a>
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
- [Project Structure](#project-structure)

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
| H1 | AI exposure increases labor market stress | Positive | Supported (β = 0.143, p < 0.10) |
| H2 | Strong social buffers protect labor income share | Positive | **Strongly supported** (β = 0.264, p < 0.001) |
| H3 | Economic resilience reduces unemployment | Negative | **Strongly supported** (β = −2.950, p < 0.001) |
| H4 | Higher inequality amplifies labor market stress | Positive | **Strongly supported** (β = 0.100, p < 0.001) |
| H5 | Human capital buffers unemployment | Negative | Supported (β = −0.107, p < 0.10) |
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
└── institutional_buffers    5933 rows  |  7 cols   [World Bank WDI — Social Spending]
```

### Data Sources

| Source | Indicators | Coverage |
|---|---|---|
| World Bank WDI API (`wbgapi`) | GDP per capita, Gini index, unemployment, trade openness, R&D expenditure, employment shares | 263 countries, 2000–2025 |
| ILOSTAT REST API | Labor income share, working poverty rate, youth unemployment, youth LFP | 186 countries, 2000–2025 |
| Oxford Insights Government AI Readiness Index | AI readiness score, digital human capital, government AI strategy | 70 countries, anchored 2022 |
| World Bank WDI — Social Spending | Health expenditure, education expenditure, fiscal balance | 253 countries, 2000–2025 |

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
    ...
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

$$\text{AI\_Exposure}_{i,t} = \text{AI\_Readiness\_Score}_{i,t} \times \text{Employment\_Share\_Services}_{i,t}$$

**Tech Vulnerability Index** — captures structural displacement risk:

$$\text{TVI}_{i,t} = \text{AI\_Exposure}_{i,t} \times \left(1 - \frac{\text{Social\_Buffer}_{i,t}}{100}\right)$$

**Social Buffer Index** — composite institutional protection score:

$$\text{SBI}_{i,t} = \frac{1}{3}\left(\text{Health\_Exp}_{i,t} + \text{Education\_Exp}_{i,t} + \text{Govt\_Exp}_{i,t}\right)_{\text{Norm}}$$

Total engineered features: **82 variables** including rolling means (MA3), 1-year and 3-year lags, regional interaction terms, and income group dummies.

---

### 3. Two-Way Fixed Effects Panel Regression

The core econometric specification absorbs both unobserved country-level heterogeneity (geography, historical institutions) and global time shocks (financial crises, pandemic, frontier AI breakthroughs):

$$Y_{i,t} = \beta_0 + \beta_1(\text{AI\_Exposure}_{i,t}) + \beta_2(\text{Tech\_Vulnerability}_{i,t}) + \gamma \mathbf{X}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}$$

Where:
- $Y_{i,t}$ ∈ {Labor Income Share, Unemployment Rate, Labor Market Stress}
- $\alpha_i$ = country fixed effects (time-invariant unobservables)
- $\delta_t$ = year fixed effects (global macro shocks)
- $\mathbf{X}_{i,t}$ = vector of time-varying controls: Gini index, GDP growth, trade openness, government expenditure, human capital index, economic resilience
- Standard errors clustered at the country level to control for serial correlation and heteroskedasticity

**Model estimated using:** `linearmodels.PanelOLS` with entity and time effects

---

### 4. Endogeneity & Robustness

Wealthy countries adopt AI faster — creating reverse causality bias in OLS. We address this via:

**Hausman Test** — formally confirms fixed effects dominate random effects:

| Dependent Variable | FE R² (Within) | RE R² | Hausman Statistic | p-value | Verdict |
|---|---|---|---|---|---|
| Labor Income Share | 0.0704 | 0.4775 | 69.31 | 0.000 | **Use Fixed Effects** |
| Unemployment Rate | 0.0833 | 0.1163 | 69.22 | 0.000 | **Use Fixed Effects** |
| Labor Market Stress | 0.2136 | 0.2026 | 82.57 | 0.000 | **Use Fixed Effects** |

**IV2SLS Robustness** — Instrumental Variables with lagged regressors as instruments, confirming TWFE directional consistency across all specifications.

**Regional Robustness** — TWFE re-estimated separately across 7 World Bank regions confirming South Asia significance (β = −0.452, p = 0.012) and North America marginal significance (β = 0.432, p = 0.077).

---

## Key Findings

### Finding 1 — Social Buffers Are the Primary Stabilizer of Labor Income

$$\hat{\beta}_{\text{Social Buffer}} = +0.264 \quad (p < 0.001, \text{ R}^2_{\text{within}} = 0.0449)$$

A one-unit increase in the Social Buffer Index raises labor income share by **0.264 percentage points**, net of country and year fixed effects. This is the single strongest significant predictor in the labor income share model — stronger than AI exposure, GDP growth, or trade openness.

---

### Finding 2 — Economic Resilience Is the Most Powerful Unemployment Buffer

$$\hat{\beta}_{\text{Economic Resilience}} = -2.950 \quad (p < 0.001)$$

$$\hat{\beta}_{\text{Govt Expenditure}} = +0.033 \quad (p < 0.001)$$

Economic resilience exerts the largest magnitude effect in the unemployment model. Notably, government expenditure **increases** unemployment at the margin — consistent with the Wagner's Law crowding-out effect in advanced economies.

---

### Finding 3 — AI Exposure Increases Labor Market Stress

$$\hat{\beta}_{\text{AI Exposure}} = +0.143 \quad (p = 0.084)$$

AI exposure exerts a **positive, marginally significant** pressure on labor market stress — consistent with task displacement theory. Crucially, Tech Vulnerability (AI exposure without institutional buffers) **significantly amplifies** this stress:

$$\hat{\beta}_{\text{Tech Vulnerability}} = -0.214 \quad (p = 0.043)$$

The negative sign on Tech Vulnerability relative to AI Exposure reveals a **moderation effect**: countries with high AI exposure but strong buffer institutions experience significantly lower net stress than those without buffers.

---

### Finding 4 — Inequality Directly Amplifies Labor Market Stress

$$\hat{\beta}_{\text{Gini}} = +0.100 \quad (p < 0.001)$$

Higher pre-existing inequality makes labor markets structurally more fragile under AI pressure — a vicious cycle where unequal economies are least equipped to absorb automation shocks.

---

### Finding 5 — IV2SLS Confirms Social Buffer Robustness

After instrumenting for endogeneity using lagged regressors:

$$\hat{\beta}_{\text{Social Buffer}}^{\text{IV}} = +0.288 \quad (p = 0.010)$$

The IV estimate is **larger** than the TWFE estimate (+0.264), suggesting the TWFE coefficient is actually a **conservative** lower bound — the true causal effect of social protection on labor income stability is at least as large.

---

### Finding 6 — Top XGBoost Predictors Confirm Econometric Findings

| Rank | Feature | Importance |
|---|---|---|
| 1 | Labor Income Share | 30.6% |
| 2 | Labor Income Share (MA3) | 18.1% |
| 3 | Gini Index | 11.9% |
| 4 | Gini Index (Lag 1) | 7.3% |
| 5 | AI Exposure × ECS Region | 5.8% |
| 6 | Region: Europe & Central Asia | 4.3% |
| 7 | Social Buffer Index | 2.8% |

Labor income share and the Gini index together account for **nearly 50%** of XGBoost predictive power — confirming their centrality in the HISI construction.

---

## HISI Index

### Mathematical Formulation

The **Human Income Stability Index (HISI)** is a novel composite metric capturing a country's ability to maintain equitable income distribution under AI-driven structural transformation:

$$\text{HISI}_{i,t} = w_1 \cdot \left(\frac{\text{Labor\_Share}_{i,t}}{\text{Gini}_{i,t}}\right)_{\text{Norm}} + w_2 \cdot (\text{Social\_Protection\_Score}_{i,t})_{\text{Norm}} - w_3 \cdot (\text{AI\_Displacement\_Risk}_{i,t})_{\text{Norm}}$$

**Weights** determined via Principal Component Analysis (PCA) — mathematically grounded, not arbitrarily assigned:

| Component | Weight | Interpretation |
|---|---|---|
| $w_1$ — Labor Equity Ratio | 0.40 | Labor share relative to inequality |
| $w_2$ — Social Protection Score | 0.35 | Institutional safety net strength |
| $w_3$ — AI Displacement Risk | 0.25 | Structural automation exposure |

**HISI scale:** 0 (maximum instability) to 100 (maximum stability)

### HISI Score Range

**Global Range: 19.45 → 88.52**

| Rank | Country | Avg HISI (2000–2025) | Cluster |
|---|---|---|---|
| 1 | 🇮🇸 Iceland | 88.52 | The Wins |
| 2 | 🇸🇮 Slovenia | 88.12 | The Wins |
| 3 | 🇧🇪 Belgium | 85.32 | The Wins |
| 4 | 🇩🇰 Denmark | 82.79 | The Wins |
| 5 | 🇳🇱 Netherlands | 78.88 | The Wins |
| 6 | 🇫🇮 Finland | 75.58 | The Wins |
| 7 | 🇸🇪 Sweden | 75.36 | The Wins |
| 8 | 🇦🇹 Austria | 75.01 | The Wins |
| ... | ... | ... | ... |
| 261 | 🇹🇯 Tajikistan | 23.30 | The Falls |
| 262 | 🇲🇽 Mexico | 23.20 | The Adapters |
| 263 | 🇻🇪 Venezuela | 21.47 | The Adapters |
| 264 | 🇶🇦 Qatar | 19.45 | The Adapters |

---

## Cluster Analysis

Countries are segmented dynamically using **K-Means clustering** on HISI component scores:

### The Wins (90 country-trajectories)
*High Digital Capital + Stable HISI + Strong Institutional Buffers*

Nordic economies, Western Europe, Australia, Canada. These countries combine strong labor protections, high social spending, and managed AI adoption curves. **Iceland, Slovenia, Belgium, Denmark, Netherlands** lead this group.

### The Falls (196 country-trajectories)
*High Task Displacement Risk + Weak Institutional Buffers*

Sub-Saharan Africa, parts of Southeast Asia, fragile states. Characterized by high informal employment exposure, thin social safety nets, and low AI governance readiness. Most vulnerable to uncushioned automation shocks.

### The Adapters (169 country-trajectories)
*High AI Exposure + Emerging Institutional Responses*

A heterogeneous group including emerging markets with growing digital sectors but lagging social infrastructure. **India, Czech Republic, Moldova** appear here — high AI exposure but building institutional responses. The critical policy battleground.

---

## Forecasts to 2050

XGBoost regressor trained on 2000–2022 data with **expanding-window cross-validation** (respecting temporal ordering) forecasts HISI trajectories under two structural scenarios:

### Scenario A — Aggressive Automation
*Accelerated AI adoption curve with stagnating social protection expenditures*

### Scenario B — Equitable Adaptation
*Balanced AI scaling paired with universal digital safety nets*

| Horizon | Aggressive Automation | Equitable Adaptation | Gap |
|---|---|---|---|
| 2030 | 44.39 | 45.71 | +1.32 |
| 2050 | 42.63 | 48.54 | **+5.90** |

**The divergence widens dramatically over time.** By 2050, the policy choice between aggressive automation and equitable adaptation creates a **5.9-point HISI gap** globally — equivalent to the difference between a stable lower-middle income economy and a fragile low-income economy on our index.

The Aggressive Automation scenario shows a **declining HISI trajectory** from 2030 onwards (44.39 → 42.63), confirming that uncushioned AI diffusion erodes global income stability in the long run.

---

## Pipeline Architecture

```
economics-of-abundant-intelligence/
│
├── config.py                          # Central config: all paths, API codes, constants
│
├── data/
│   ├── raw/
│   │   ├── world_bank/wb_ingest.py    # World Bank WDI API ingestion (wbgapi)
│   │   ├── ilo/ilo_ingest.py          # ILOSTAT REST API ingestion
│   │   └── stanford_ai/ai_ingest.py   # AI Vibrancy + Institutional Buffers
│   ├── imputed/
│   │   └── impute.py                  # 3-stage imputation: rolling → KNN → threshold
│   └── features/
│       └── build_features.py          # 82-feature engineering pipeline
│
├── database/
│   ├── schemas/schema.py              # SQLite schema: 5 tables, PKs, FKs, indexes
│   └── hisi_panel.db                  # Production database (8.83 MB)
│
├── models/
│   ├── panel_econometrics.py          # TWFE + cluster-robust SE (linearmodels)
│   ├── gmm_robustness.py              # IV2SLS endogeneity robustness
│   ├── hisi_construction.py           # PCA weights + HISI computation + K-Means
│   ├── forecasting.py                 # XGBoost + expanding-window CV + scenarios
│   ├── results/                       # All regression tables, cluster CSVs, forecasts
│   └── saved/xgb_hisi.json            # Serialized XGBoost model (2.99 MB)
│
└── dashboard/
    └── app.py                         # Streamlit multi-page dashboard (49 KB)
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

### 3. Initialize the database

```bash
python database/schemas/schema.py
```

### 4. Run the full ingestion pipeline

```bash
python data/raw/world_bank/wb_ingest.py
python data/raw/ilo/ilo_ingest.py
python data/raw/stanford_ai/ai_ingest.py
```

### 5. Impute and build features

```bash
python data/imputed/impute.py
python data/features/build_features.py
```

### 6. Run econometric models and construct HISI

```bash
python models/panel_econometrics.py
python models/gmm_robustness.py
python models/hisi_construction.py
python models/forecasting.py
```

### 7. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

---

## Technical Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| Database | SQLite via SQLAlchemy 2.0 |
| Data APIs | `wbgapi` (World Bank), ILOSTAT REST |
| Econometrics | `linearmodels` (TWFE, IV2SLS), `statsmodels` |
| Imputation | `scikit-learn` KNNImputer |
| Machine Learning | `xgboost` 2.0 |
| Dashboard | `streamlit` + `plotly` |
| Visualization | `matplotlib`, `seaborn`, `plotly` |
| Environment | Anaconda, conda virtual environment |

---

## Economic Interpretation & Policy Implications

**1. Social protection is not a luxury — it is a structural stabilizer.** The IV2SLS estimate (β = +0.288, p = 0.010) confirms that social buffer institutions causally protect labor income share even after controlling for reverse causality. Countries dismantling safety nets under fiscal austerity are compounding their AI vulnerability.

**2. Inequality is a force multiplier for automation risk.** The Gini coefficient is the third most important XGBoost predictor (11.9% importance) and significant in TWFE (β = +0.100, p < 0.001). Unequal societies are structurally less resilient to AI-driven disruption — creating a risk spiral where inequality feeds instability feeds more inequality.

**3. The 2050 divergence is a policy choice, not a technological inevitability.** The 5.9-point HISI gap between automation and adaptation scenarios by 2050 is not driven by technological trajectories — it is driven entirely by the presence or absence of institutional responses. The economics of abundant intelligence has a clear prescription: invest in the buffers.

**4. South Asia is the highest-risk significant region.** The regional robustness analysis identifies South Asia as the only region where AI exposure is statistically significant (β = −0.452, p = 0.012) — and in the opposite direction to theory, suggesting possible positive structural transformation effects for India and Bangladesh under current trajectories. Warrants deeper investigation.

---

## Citation

```bibtex
@misc{chatterjee2026hisi,
  author       = {Chatterjee, Daipayan},
  title        = {The Economics of Abundant Intelligence: Who Wins, Who Falls,
                  and Who Adapts? Global Evidence on Income Stability and
                  Career Sustainability in the AI Era},
  year         = {2026},
  institution  = {St. Xavier's University, Kolkata},
  note         = {M.Sc. Economics Research Project},
  url          = {https://github.com/dchatterjee01-prog/economics-of-abundant-intelligence}
}
```

---

## Author

**Daipayan Chatterjee**
M.Sc. Economics | Specialization: Quantitative Economics & Econometrics


[![GitHub](https://img.shields.io/badge/GitHub-dchatterjee01--prog-black?style=flat&logo=github)](https://github.com/dchatterjee01-prog)

---

*This research pipeline was built entirely from scratch as an independent quantitative research project, combining production-grade data engineering, rigorous econometric methodology, and machine learning forecasting — demonstrating end-to-end capability across the full quantitative research stack.*
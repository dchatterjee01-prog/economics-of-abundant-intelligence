# dashboard/app.py
# Phase 6 — Production-Grade HISI Intelligence Dashboard
# Run: streamlit run dashboard/app.py

# NOTE: sys.stdout wrapper removed — it crashes Streamlit (stdout is already
# redirected by Streamlit's runtime). The wrapper is only needed for terminal scripts.

import io, sys
import os, warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from xgboost import XGBRegressor

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT  = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HISI_PATH     = os.path.join(PROJECT_ROOT, "data",   "features",  "hisi_panel.csv")
FEAT_PATH     = os.path.join(PROJECT_ROOT, "data",   "features",  "panel_features.csv")
CLUSTER_PATH  = os.path.join(PROJECT_ROOT, "models", "results",   "country_avg_hisi.csv")
FORECAST_PATH = os.path.join(PROJECT_ROOT, "models", "results",   "forecast_2050.csv")
FEAT_IMP_PATH = os.path.join(PROJECT_ROOT, "models", "results",   "feature_importance.csv")
MODEL_PATH    = os.path.join(PROJECT_ROOT, "models", "saved",     "xgb_hisi.json")
FEAT_COL_PATH = os.path.join(PROJECT_ROOT, "models", "saved",     "feature_cols.txt")
RESULTS_DIR   = os.path.join(PROJECT_ROOT, "models", "results")

WB_AGGREGATES = {
    "EAP","EAS","ECS","LAC","LCN","MEA","NAC","SAS","SSA","SSF",
    "TEA","TLA","TSA","CSS","OSS","PSS","LTE","EMU","HIC","LIC",
    "LMC","MIC","UMC","WLD","ARB","CEB","EAR","FCS","HPC","IBD",
    "IBT","IDA","IDX","LDC","OED","PRE","PST","TEC","ECA","IDB",
}

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
PALETTE = {
    "ink":       "#0D0F14",
    "panel":     "#13161E",
    "card":      "#1C2030",
    "border":    "#2A2F42",
    "accent":    "#00D4AA",
    "accent2":   "#7B61FF",
    "danger":    "#FF4D6D",
    "warn":      "#FFB800",
    "text":      "#E8EAF0",
    "muted":     "#7A8099",
    "wins":      "#00D4AA",
    "adapters":  "#FFB800",
    "falls":     "#FF4D6D",
}

st.set_page_config(
    page_title="HISI Intelligence Platform",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Playfair+Display:wght@700&display=swap');

html, body, [class*="css"], .stApp {{
    background-color: {PALETTE['ink']} !important;
    color: {PALETTE['text']} !important;
    font-family: 'Space Grotesk', sans-serif !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
    background: {PALETTE['panel']} !important;
    border-right: 1px solid {PALETTE['border']} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {PALETTE['text']} !important;
}}

/* Hide default streamlit chrome */
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ padding: 1.5rem 2.5rem !important; max-width: 100% !important; }}

/* Cards */
.kpi-card {{
    background: {PALETTE['card']};
    border: 1px solid {PALETTE['border']};
    border-top: 2px solid {PALETTE['accent']};
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {PALETTE['accent']}, {PALETTE['accent2']});
}}
.kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 600;
    color: {PALETTE['accent']};
    line-height: 1;
    margin-bottom: 0.3rem;
}}
.kpi-label {{
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: {PALETTE['muted']};
}}
.kpi-delta-pos {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: {PALETTE['wins']};
}}
.kpi-delta-neg {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: {PALETTE['danger']};
}}

/* Section headers */
.section-eyebrow {{
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: {PALETTE['accent']};
    margin-bottom: 0.3rem;
}}
.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: {PALETTE['text']};
    margin-bottom: 0.1rem;
}}
.section-sub {{
    font-size: 0.85rem;
    color: {PALETTE['muted']};
    margin-bottom: 1.5rem;
}}

/* Hero banner */
.hero {{
    background: linear-gradient(135deg, {PALETTE['panel']} 0%, #1a1f35 50%, {PALETTE['card']} 100%);
    border: 1px solid {PALETTE['border']};
    border-left: 4px solid {PALETTE['accent']};
    border-radius: 10px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}}
.hero::after {{
    content: '◈';
    position: absolute;
    right: 2rem; top: 1rem;
    font-size: 6rem;
    color: {PALETTE['accent']};
    opacity: 0.06;
    line-height: 1;
}}
.hero-title {{
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: {PALETTE['text']};
    margin-bottom: 0.4rem;
    line-height: 1.2;
}}
.hero-sub {{
    font-size: 0.9rem;
    color: {PALETTE['muted']};
    max-width: 620px;
    line-height: 1.6;
}}
.hero-tag {{
    display: inline-block;
    background: rgba(0,212,170,0.12);
    border: 1px solid rgba(0,212,170,0.3);
    color: {PALETTE['accent']};
    border-radius: 4px;
    padding: 0.15rem 0.6rem;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-right: 0.5rem;
    margin-bottom: 0.8rem;
}}

/* Cluster chips */
.chip-wins     {{ background: rgba(0,212,170,0.15); border:1px solid {PALETTE['wins']};
                  color:{PALETTE['wins']}; border-radius:20px; padding:0.2rem 0.7rem;
                  font-size:0.75rem; font-weight:600; display:inline-block; }}
.chip-adapters {{ background: rgba(255,184,0,0.15); border:1px solid {PALETTE['adapters']};
                  color:{PALETTE['adapters']}; border-radius:20px; padding:0.2rem 0.7rem;
                  font-size:0.75rem; font-weight:600; display:inline-block; }}
.chip-falls    {{ background: rgba(255,77,109,0.15); border:1px solid {PALETTE['falls']};
                  color:{PALETTE['falls']}; border-radius:20px; padding:0.2rem 0.7rem;
                  font-size:0.75rem; font-weight:600; display:inline-block; }}

/* Divider */
.div-accent {{
    height: 1px;
    background: linear-gradient(90deg, {PALETTE['accent']}44, transparent);
    margin: 1.5rem 0;
}}

/* Table styling */
.dataframe thead th {{
    background: {PALETTE['panel']} !important;
    color: {PALETTE['accent']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid {PALETTE['border']} !important;
}}
.dataframe tbody tr {{ background: {PALETTE['card']} !important; }}
.dataframe tbody tr:hover {{ background: {PALETTE['panel']} !important; }}
.dataframe tbody td {{
    color: {PALETTE['text']} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    border-bottom: 1px solid {PALETTE['border']} !important;
}}

/* Slider */
.stSlider > div > div > div {{ background: {PALETTE['accent']} !important; }}
.stSlider [data-baseweb="slider"] {{ color: {PALETTE['accent']} !important; }}

/* Radio / selectbox */
.stRadio label, .stSelectbox label {{
    color: {PALETTE['muted']} !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}}
div[data-baseweb="select"] {{
    background: {PALETTE['card']} !important;
    border-color: {PALETTE['border']} !important;
}}
div[data-baseweb="select"] * {{ color: {PALETTE['text']} !important; }}

/* Nav pills in sidebar */
.stRadio div[role="radiogroup"] label {{
    background: {PALETTE['card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
    margin-bottom: 0.3rem;
    cursor: pointer;
    transition: all 0.2s;
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-size: 0.85rem !important;
}}

/* Info boxes */
.insight-box {{
    background: rgba(0,212,170,0.07);
    border: 1px solid rgba(0,212,170,0.25);
    border-left: 3px solid {PALETTE['accent']};
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin: 0.8rem 0;
    font-size: 0.84rem;
    line-height: 1.6;
    color: {PALETTE['text']};
}}
.warning-box {{
    background: rgba(255,184,0,0.07);
    border: 1px solid rgba(255,184,0,0.25);
    border-left: 3px solid {PALETTE['warn']};
    border-radius: 6px;
    padding: 0.9rem 1.1rem;
    margin: 0.8rem 0;
    font-size: 0.84rem;
    color: {PALETTE['text']};
}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PLOTLY THEME
# ══════════════════════════════════════════════════════════════════════════════
PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font=dict(family="Space Grotesk, sans-serif", color=PALETTE["text"], size=12),
    title_font=dict(family="Space Grotesk, sans-serif", size=14,
                    color=PALETTE["text"]),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=PALETTE["border"],
                borderwidth=1, font=dict(size=11)),
    xaxis=dict(gridcolor=PALETTE["border"], linecolor=PALETTE["border"],
               tickfont=dict(size=10, family="JetBrains Mono")),
    yaxis=dict(gridcolor=PALETTE["border"], linecolor=PALETTE["border"],
               tickfont=dict(size=10, family="JetBrains Mono")),
    margin=dict(l=10, r=10, t=45, b=10),
)
CHOROPLETH_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    geo=dict(
        bgcolor="rgba(0,0,0,0)",
        showframe=False,
        showcoastlines=True,
        coastlinecolor=PALETTE["border"],
        showland=True, landcolor="#1C2030",
        showocean=True, oceancolor="#13161E",
        showlakes=False,
        projection_type="natural earth",
    ),
    font=dict(family="Space Grotesk", color=PALETTE["text"]),
    margin=dict(l=0, r=0, t=40, b=0),
)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADERS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_hisi():
    df = pd.read_csv(HISI_PATH)
    return df[~df["iso_alpha3"].isin(WB_AGGREGATES)]

@st.cache_data
def load_clusters():
    df = pd.read_csv(CLUSTER_PATH)
    # column saved as 'avg_hisi' — normalize to 'hisi_score' for dashboard
    if "avg_hisi" in df.columns and "hisi_score" not in df.columns:
        df = df.rename(columns={"avg_hisi": "hisi_score"})
    return df[~df["iso_alpha3"].isin(WB_AGGREGATES)]

@st.cache_data
def load_forecast():
    df = pd.read_csv(FORECAST_PATH)
    return df[~df["iso_alpha3"].isin(WB_AGGREGATES)]

@st.cache_data
def load_feat_imp():
    return pd.read_csv(FEAT_IMP_PATH)

@st.cache_data
def load_features():
    df = pd.read_csv(FEAT_PATH)
    return df[~df["iso_alpha3"].isin(WB_AGGREGATES)]

@st.cache_resource
def load_model():
    m = XGBRegressor()
    m.load_model(MODEL_PATH)
    with open(FEAT_COL_PATH) as f:
        cols = [l.strip() for l in f if l.strip()]
    return m, cols

@st.cache_data
def load_twfe():
    results = {}
    depvar_map = {
        "Labor Income Share":  "labor_income_share_pct",
        "Unemployment Rate":   "unemployment_rate",
        "Labor Market Stress": "labor_market_stress",
    }

    # Try individual files first
    for label, dv in depvar_map.items():
        for fname in [f"twfe_{dv}.csv", f"{dv}_twfe.csv", f"{dv}.csv"]:
            fp = os.path.join(RESULTS_DIR, fname)
            if os.path.exists(fp):
                results[label] = pd.read_csv(fp)
                break

    if len(results) == 3:
        return results

    # Fallback: combined file — split by dependent_var column
    combined_path = os.path.join(RESULTS_DIR, "twfe_regression_results.csv")
    if not os.path.exists(combined_path):
        return results if results else {}

    df = pd.read_csv(combined_path)
    for label, dv in depvar_map.items():
        if label not in results:  # Only populate if not already found individually
            subset = df[df["dependent_var"] == dv].reset_index(drop=True)
            if not subset.empty:
                results[label] = subset

    return results

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding:1rem 0 0.5rem'>
      <div style='font-size:1.4rem;font-weight:700;color:{PALETTE["accent"]};
                  font-family:Space Grotesk;letter-spacing:-0.02em'>◈ HISI</div>
      <div style='font-size:0.72rem;color:{PALETTE["muted"]};
                  letter-spacing:0.12em;text-transform:uppercase;
                  margin-top:0.1rem'>Intelligence Platform</div>
    </div>
    <div style='height:1px;background:{PALETTE["border"]};margin:0.8rem 0'></div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "◈  Global Overview",
        "⬡  Policy Simulator",
        "⊕  Forecast 2050",
        "∿  Econometric Lab",
    ], label_visibility="collapsed")

    st.markdown(f"""
    <div style='height:1px;background:{PALETTE["border"]};margin:1rem 0'></div>
    <div style='font-size:0.68rem;color:{PALETTE["muted"]};line-height:1.8'>
      <div style='color:{PALETTE["accent"]};font-weight:600;
                  letter-spacing:0.1em;font-size:0.65rem;
                  text-transform:uppercase;margin-bottom:0.4rem'>
        Research Pipeline
      </div>
      264 countries · 26 years<br>
      6,774 country-year obs<br>
      XGBoost · CV R²&nbsp;=&nbsp;0.990<br>
      TWFE · AB-GMM · IV-2SLS<br>
      <br>
      <span style='color:{PALETTE["text"]};font-weight:500'>Daipayan Chatterjee</span><br>
      <span style='color:{PALETTE["muted"]}'>M.Sc. Economics</span><br>
      <span style='color:{PALETTE["muted"]}'>GitHub: </span><a href='https://github.com/dchatterjee01-prog' target='_blank' style='color:{PALETTE["accent"]};text-decoration:none;font-family:JetBrains Mono'>dchatterjee01-prog</a>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — GLOBAL OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if "Global Overview" in page:

    hisi_df    = load_hisi()
    cluster_df = load_clusters()
    latest     = hisi_df["year"].max()
    latest_df  = hisi_df[hisi_df["year"] == latest]

    # Hero
    n_wins = len(latest_df[latest_df["cluster_label"] == "The Wins"])
    n_fall = len(latest_df[latest_df["cluster_label"] == "The Falls"])
    st.markdown(f"""
    <div class="hero">
      <div style='margin-bottom:0.8rem'>
        <span class="hero-tag">Global Evidence</span>
        <span class="hero-tag">2000–2025</span>
        <span class="hero-tag">264 Economies</span>
      </div>
      <div class="hero-title">The Economics of Abundant Intelligence</div>
      <div class="hero-title" style='color:{PALETTE["accent"]}'>
        Who Wins, Who Falls, and Who Adapts?
      </div>
      <div class="hero-sub" style='margin-top:0.7rem'>
        The Human Income Stability Index (HISI) tracks income security and career
        sustainability across the AI transition. In {latest}, only
        <strong style='color:{PALETTE["wins"]}'>{n_wins} economies</strong> are
        positioned to win — while
        <strong style='color:{PALETTE["falls"]}'>{n_fall} are falling behind</strong>.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    global_hisi  = latest_df["hisi_score"].mean()
    global_ai    = latest_df["ai_exposure_proxy"].mean() if "ai_exposure_proxy" in latest_df else 0
    global_buf   = latest_df["social_buffer_index"].mean() if "social_buffer_index" in latest_df else 0
    n_adapters   = len(latest_df[latest_df["cluster_label"] == "The Adapters"])

    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_data = [
        (k1, f"{global_hisi:.1f}",  "Global HISI",         "/100",   "+0.0"),
        (k2, f"{n_wins}",           "The Wins",            "nations", "▲"),
        (k3, f"{n_adapters}",       "The Adapters",        "nations", "—"),
        (k4, f"{n_fall}",           "The Falls",           "nations", "▼"),
        (k5, f"{global_ai:.1f}",    "AI Exposure Index",   "avg",     "↑5%/yr"),
    ]
    for col, val, label, unit, delta in kpi_data:
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value">{val}</div>
          <div style='font-size:0.7rem;color:{PALETTE["muted"]};
                      font-family:JetBrains Mono;margin-bottom:0.15rem'>{unit}</div>
          <div class="kpi-label">{label}</div>
          <div class="kpi-delta-pos" style='margin-top:0.4rem'>{delta}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # World map
    col_left, col_right = st.columns([7, 3])

    with col_left:
        st.markdown(f"""
        <div class="section-eyebrow">Global Distribution · {latest}</div>
        <div class="section-title">HISI World Map</div>
        """, unsafe_allow_html=True)

        map_var = st.radio("Map Variable",
            ["HISI Score", "AI Exposure", "Social Buffer", "Cluster"],
            horizontal=True, key="map_radio",
            label_visibility="collapsed")

        var_map = {
            "HISI Score":    ("hisi_score",         "RdYlGn"),
            "AI Exposure":   ("ai_exposure_proxy",   "YlOrRd"),
            "Social Buffer": ("social_buffer_index", "Blues"),
        }

        if map_var == "Cluster":
            cmap   = {"The Wins": PALETTE["wins"],
                      "The Adapters": PALETTE["adapters"],
                      "The Falls": PALETTE["falls"]}
            fig_m  = px.choropleth(
                latest_df, locations="iso_alpha3", color="cluster_label",
                color_discrete_map=cmap,
                hover_name="iso_alpha3",
                hover_data={"hisi_score":":.1f","cluster_label":True},
            )
        else:
            vcol, cscale = var_map[map_var]
            fig_m = px.choropleth(
                latest_df, locations="iso_alpha3", color=vcol,
                color_continuous_scale=cscale,
                range_color=[latest_df[vcol].quantile(0.05),
                             latest_df[vcol].quantile(0.95)],
                hover_name="iso_alpha3",
                hover_data={"hisi_score":":.1f"},
                labels={vcol: map_var},
            )
            fig_m.update_coloraxes(colorbar=dict(
                thickness=10, len=0.7, x=1.01,
                tickfont=dict(size=9, family="JetBrains Mono",
                              color=PALETTE["text"]),
                title=dict(font=dict(size=9, color=PALETTE["muted"])),
            ))

        fig_m.update_traces(marker_line_width=0.3,
                            marker_line_color=PALETTE["border"])
        fig_m.update_layout(**CHOROPLETH_LAYOUT, height=420)
        st.plotly_chart(fig_m, use_container_width=True)

    with col_right:
        st.markdown(f"""
        <div class="section-eyebrow">Cluster Breakdown · {latest}</div>
        <div class="section-title" style='font-size:1.2rem'>Who's Where</div>
        <div style='height:0.8rem'></div>
        """, unsafe_allow_html=True)

        for label, color, chip_class, desc in [
            ("The Wins",     PALETTE["wins"],     "chip-wins",
             "High HISI · Strong institutions · AI-ready"),
            ("The Adapters", PALETTE["adapters"], "chip-adapters",
             "Medium HISI · Exposed but buffered"),
            ("The Falls",    PALETTE["falls"],    "chip-falls",
             "Low HISI · High risk · Weak safety nets"),
        ]:
            n = len(latest_df[latest_df["cluster_label"] == label])
            pct = n / len(latest_df) * 100
            st.markdown(f"""
            <div style='background:{PALETTE["card"]};border:1px solid {PALETTE["border"]};
                        border-left:3px solid {color};border-radius:8px;
                        padding:0.9rem 1rem;margin-bottom:0.6rem'>
              <span class="{chip_class}">{label}</span>
              <div style='font-family:JetBrains Mono;font-size:1.5rem;
                          font-weight:600;color:{color};margin:0.4rem 0 0.1rem'>
                {n} <span style='font-size:0.9rem;color:{PALETTE["muted"]}'>
                ({pct:.0f}%)</span>
              </div>
              <div style='font-size:0.75rem;color:{PALETTE["muted"]}'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        # Scatter: HISI vs AI Exposure
        if "ai_exposure_proxy" in latest_df.columns:
            fig_sc = px.scatter(
                latest_df.dropna(subset=["ai_exposure_proxy","hisi_score"]),
                x="ai_exposure_proxy", y="hisi_score",
                color="cluster_label",
                color_discrete_map={
                    "The Wins": PALETTE["wins"],
                    "The Adapters": PALETTE["adapters"],
                    "The Falls": PALETTE["falls"],
                },
                hover_name="iso_alpha3",
                size_max=6,
                labels={"ai_exposure_proxy":"AI Exposure","hisi_score":"HISI"},
                title="HISI vs AI Exposure"
            )
            fig_sc.update_traces(marker=dict(size=5, opacity=0.75))
            fig_sc.update_layout(**PLOTLY_BASE, height=220,
                                  showlegend=False,
                                  title_font_size=11)
            st.plotly_chart(fig_sc, use_container_width=True)

    # Top / Bottom league table
    st.markdown('<div class="div-accent"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="section-eyebrow">Rankings</div>
    <div class="section-title">HISI League Table — {latest}</div>
    <div class="section-sub">Country-level scores ranked by Human Income Stability Index</div>
    """, unsafe_allow_html=True)

    t1, t2 = st.columns(2)
    rank_df = latest_df[["iso_alpha3","hisi_score","cluster_label"]]\
                .sort_values("hisi_score", ascending=False).reset_index(drop=True)
    rank_df.index += 1

    def colour_cluster(val):
        m = {"The Wins": PALETTE["wins"],
             "The Adapters": PALETTE["adapters"],
             "The Falls": PALETTE["falls"]}
        c = m.get(val, PALETTE["text"])
        return f"color: {c}; font-weight: 600"

    with t1:
        st.markdown(f"<div style='color:{PALETTE['wins']};font-size:0.75rem;"
                    f"font-weight:600;letter-spacing:0.1em;text-transform:uppercase;"
                    f"margin-bottom:0.4rem'>▲ Top 20 Performers</div>",
                    unsafe_allow_html=True)
        top20 = rank_df.head(20)[["iso_alpha3","hisi_score","cluster_label"]].copy()
        top20["hisi_score"] = top20["hisi_score"].round(1)
        st.dataframe(
            top20.style.applymap(colour_cluster, subset=["cluster_label"]),
            use_container_width=True, height=560,
        )
    with t2:
        st.markdown(f"<div style='color:{PALETTE['falls']};font-size:0.75rem;"
                    f"font-weight:600;letter-spacing:0.1em;text-transform:uppercase;"
                    f"margin-bottom:0.4rem'>▼ Bottom 20 — At Risk</div>",
                    unsafe_allow_html=True)
        bot20 = rank_df.tail(20).sort_values("hisi_score")[
            ["iso_alpha3","hisi_score","cluster_label"]].copy()
        bot20["hisi_score"] = bot20["hisi_score"].round(1)
        st.dataframe(
            bot20.style.applymap(colour_cluster, subset=["cluster_label"]),
            use_container_width=True, height=560,
        )

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — POLICY SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif "Policy Simulator" in page:

    hisi_df  = load_hisi()
    feat_df  = load_features()
    model, feat_cols = load_model()
    latest   = hisi_df["year"].max()
    year_df  = hisi_df[hisi_df["year"] == latest]

    st.markdown(f"""
    <div class="section-eyebrow">Interactive Scenario Tool</div>
    <div class="section-title">Policy Lever Simulator</div>
    <div class="section-sub">
      Select a country and adjust policy parameters.
      The XGBoost model (CV R²&nbsp;=&nbsp;0.990) predicts the resulting HISI score in real time.
    </div>
    """, unsafe_allow_html=True)

    sim_l, sim_r = st.columns([3, 5])

    with sim_l:
        countries = sorted(year_df["iso_alpha3"].unique())
        default   = countries.index("IND") if "IND" in countries else 0
        sel       = st.selectbox("Country", countries, index=default)

        base = feat_df[feat_df["iso_alpha3"] == sel].sort_values("year").iloc[-1]

        def safe(col, default=0.0, lo=0.0, hi=100.0):
            try: return float(np.clip(base[col], lo, hi))
            except: return default

        st.markdown(f"""
        <div style='background:{PALETTE["card"]};border:1px solid {PALETTE["border"]};
                    border-radius:8px;padding:1rem 1.1rem;margin:0.8rem 0'>
          <div style='font-size:0.68rem;color:{PALETTE["muted"]};
                      letter-spacing:0.12em;text-transform:uppercase;
                      margin-bottom:0.7rem'>Baseline values ({int(base["year"])})</div>
          <div style='font-family:JetBrains Mono;font-size:0.8rem;
                      line-height:2;color:{PALETTE["text"]}'>
            AI Exposure&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{safe("ai_exposure_proxy"):.1f}<br>
            Social Buffer&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{safe("social_buffer_index", lo=0, hi=100):.1f}<br>
            R&amp;D % GDP&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{safe("rd_expenditure_pct_gdp", lo=0, hi=20):.2f}<br>
            GDP Growth&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{safe("gdp_growth_pct", lo=-30, hi=30):.2f}<br>
            Trade Openness&nbsp;&nbsp;&nbsp;{safe("trade_openness_pct_gdp", lo=0, hi=300):.1f}
          </div>
        </div>
        """, unsafe_allow_html=True)

    with sim_r:
        st.markdown(f"<div style='color:{PALETTE['accent']};font-size:0.72rem;"
                    f"letter-spacing:0.12em;text-transform:uppercase;font-weight:600;"
                    f"margin-bottom:0.6rem'>Adjust policy levers</div>",
                    unsafe_allow_html=True)

        s1, s2 = st.columns(2)
        with s1:
            sim_ai = st.slider("AI Exposure Intensity", 0.0, 100.0,
                               safe("ai_exposure_proxy"), 0.5,
                               help="Composite AI penetration in labor market")
            sim_social = st.slider("Social Spending Index", 0.0, 60.0,
                                   safe("social_buffer_index", lo=0, hi=60), 0.5,
                                   help="Social protection + health + education")
        with s2:
            sim_rd = st.slider("R&D Investment (% GDP)", 0.0, 8.0,
                               safe("rd_expenditure_pct_gdp", lo=0, hi=8), 0.05,
                               help="R&D expenditure as % of GDP")
            sim_gdp = st.slider("GDP Growth (%)", -5.0, 12.0,
                                safe("gdp_growth_pct", lo=-5, hi=12), 0.1,
                                help="Annual GDP growth rate")

        # Predict
        pred_row = pd.DataFrame([base[feat_cols].fillna(0)])
        for col, val in [("ai_exposure_proxy", sim_ai),
                         ("social_buffer_index", sim_social),
                         ("rd_expenditure_pct_gdp", sim_rd),
                         ("gdp_growth_pct", sim_gdp)]:
            if col in pred_row.columns:
                pred_row[col] = val

        pred_hisi = float(np.clip(model.predict(pred_row)[0], 0, 100))
        curr_row  = year_df[year_df["iso_alpha3"] == sel]
        curr_hisi = float(curr_row["hisi_score"].values[0]) if not curr_row.empty else pred_hisi
        delta     = pred_hisi - curr_hisi

        if pred_hisi >= 55:
            cluster_sim = ("The Wins", PALETTE["wins"], "chip-wins")
        elif pred_hisi >= 38:
            cluster_sim = ("The Adapters", PALETTE["adapters"], "chip-adapters")
        else:
            cluster_sim = ("The Falls", PALETTE["falls"], "chip-falls")

        m1, m2, m3 = st.columns(3)
        m1.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">Current HISI</div>
          <div class="kpi-value" style='color:{PALETTE["muted"]}'>{curr_hisi:.1f}</div>
        </div>""", unsafe_allow_html=True)
        m2.markdown(f"""
        <div class="kpi-card" style='border-top-color:{cluster_sim[1]}'>
          <div class="kpi-label">Simulated HISI</div>
          <div class="kpi-value" style='color:{cluster_sim[1]}'>{pred_hisi:.1f}</div>
          <div class='{"kpi-delta-pos" if delta>=0 else "kpi-delta-neg"}'
               style='margin-top:0.3rem'>{delta:+.1f} pts</div>
        </div>""", unsafe_allow_html=True)
        m3.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">Cluster</div>
          <div style='margin-top:0.6rem'><span class="{cluster_sim[2]}">{cluster_sim[0]}</span></div>
        </div>""", unsafe_allow_html=True)

    # Sensitivity: sweep each lever
    st.markdown('<div class="div-accent"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="section-eyebrow">Sensitivity Analysis</div>
    <div class="section-title" style='font-size:1.2rem'>
      How each lever shifts HISI for {sel}
    </div>
    """, unsafe_allow_html=True)

    levers = {
        "AI Exposure":    ("ai_exposure_proxy",      np.linspace(0, 100, 40)),
        "Social Buffer":  ("social_buffer_index",    np.linspace(0, 60, 40)),
        "R&D % GDP":      ("rd_expenditure_pct_gdp", np.linspace(0, 8,  40)),
        "GDP Growth":     ("gdp_growth_pct",         np.linspace(-5, 12, 40)),
    }
    colors = [PALETTE["accent"], PALETTE["accent2"],
              PALETTE["warn"], PALETTE["danger"]]

    fig_sens = go.Figure()
    for (lever_name, (col, vals)), color in zip(levers.items(), colors):
        ys = []
        for v in vals:
            r = pd.DataFrame([base[feat_cols].fillna(0)])
            if col in r.columns:
                r[col] = v
            ys.append(float(np.clip(model.predict(r)[0], 0, 100)))
        fig_sens.add_trace(go.Scatter(
            x=vals, y=ys, name=lever_name,
            mode="lines", line=dict(color=color, width=2.5),
        ))

    fig_sens.update_layout(
        **PLOTLY_BASE, height=300,
        xaxis_title="Policy lever value",
        yaxis_title="Predicted HISI",
        title=f"HISI Sensitivity — {sel}",
    )
    fig_sens.update_layout(legend=dict(orientation="h", y=1.12, x=0))
    st.plotly_chart(fig_sens, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — FORECAST 2050
# ══════════════════════════════════════════════════════════════════════════════
elif "Forecast" in page:

    hisi_df     = load_hisi()
    forecast_df = load_forecast()

    st.markdown(f"""
    <div class="section-eyebrow">XGBoost Scenario Analysis</div>
    <div class="section-title">HISI Forecast 2026–2050</div>
    <div class="section-sub">
      Two policy scenarios — Aggressive Automation vs Equitable Adaptation —
      projected for 226 economies using rolling-window XGBoost (CV RMSE 1.47).
    </div>
    """, unsafe_allow_html=True)

    # Global trajectory
    hist_g = hisi_df.groupby("year")["hisi_score"].mean().reset_index()
    fc_g   = forecast_df.groupby(["year","scenario"])["hisi_forecast"].mean().reset_index()

    fig_traj = go.Figure()
    fig_traj.add_trace(go.Scatter(
        x=hist_g["year"], y=hist_g["hisi_score"],
        name="Historical", mode="lines",
        line=dict(color=PALETTE["text"], width=2.5),
    ))
    sc_colors = {"Aggressive_Automation": PALETTE["danger"],
                 "Equitable_Adaptation":  PALETTE["wins"]}
    for sc, grp in fc_g.groupby("scenario"):
        fig_traj.add_trace(go.Scatter(
            x=grp["year"], y=grp["hisi_forecast"],
            name=sc.replace("_"," "),
            mode="lines",
            line=dict(color=sc_colors[sc], width=2.5, dash="dot"),
        ))
    fig_traj.add_vline(x=2025, line_dash="dash",
                       line_color=PALETTE["muted"],
                       annotation_text="Forecast →",
                       annotation_font_color=PALETTE["muted"],
                       annotation_font_size=10)

    fig_traj.update_layout(
        **PLOTLY_BASE, height=340,
        title="Global Mean HISI — Historical & Projected",
        yaxis_title="Mean HISI Score",
        xaxis_title="Year",
    )
    fig_traj.update_layout(legend=dict(orientation="h", y=1.12, x=0))
    st.plotly_chart(fig_traj, use_container_width=True)

    # Scenario delta map
    st.markdown('<div class="div-accent"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="section-eyebrow">2050 Projection Map</div>
    <div class="section-title">Where will countries stand in 2050?</div>
    """, unsafe_allow_html=True)

    map_col1, map_col2 = st.columns([6,4])
    with map_col1:
        sc_sel = st.radio("Scenario",
            ["Aggressive Automation", "Equitable Adaptation"],
            horizontal=True, key="fc_map_sc",
            label_visibility="collapsed")
        sc_key = sc_sel.replace(" ","_")
        fc2050 = forecast_df[
            (forecast_df["scenario"]==sc_key) &
            (forecast_df["year"]==2050)
        ]
        fig_fcm = px.choropleth(
            fc2050, locations="iso_alpha3",
            color="hisi_forecast",
            color_continuous_scale="RdYlGn",
            range_color=[0,100],
            hover_name="iso_alpha3",
            hover_data={"hisi_forecast":":.1f"},
            labels={"hisi_forecast":"HISI 2050"},
        )
        fig_fcm.update_traces(marker_line_width=0.3,
                              marker_line_color=PALETTE["border"])
        fig_fcm.update_layout(**CHOROPLETH_LAYOUT, height=360)
        fig_fcm.update_coloraxes(colorbar=dict(
            thickness=10, len=0.65, x=1.01,
            tickfont=dict(size=9, family="JetBrains Mono",
                          color=PALETTE["text"]),
        ))
        st.plotly_chart(fig_fcm, use_container_width=True)

    with map_col2:
        eq = forecast_df[(forecast_df["scenario"]=="Equitable_Adaptation")&
                         (forecast_df["year"]==2050)][["iso_alpha3","hisi_forecast"]]\
               .rename(columns={"hisi_forecast":"eq"})
        ag = forecast_df[(forecast_df["scenario"]=="Aggressive_Automation")&
                         (forecast_df["year"]==2050)][["iso_alpha3","hisi_forecast"]]\
               .rename(columns={"hisi_forecast":"ag"})
        div = eq.merge(ag, on="iso_alpha3")
        div["gain"] = div["eq"] - div["ag"]
        top_gain = div.nlargest(10,"gain")[["iso_alpha3","gain"]].round(2)
        top_gain.columns = ["Country","HISI Gain (Eq-Ag)"]

        st.markdown(f"""
        <div class="section-eyebrow">Policy Dividend</div>
        <div style='font-size:1rem;font-weight:600;color:{PALETTE["text"]};
                    margin-bottom:0.8rem'>
          Top 10 countries that benefit most from Equitable Adaptation
        </div>
        """, unsafe_allow_html=True)

        fig_gain = px.bar(
            top_gain.sort_values("HISI Gain (Eq-Ag)"),
            x="HISI Gain (Eq-Ag)", y="Country",
            orientation="h",
            color="HISI Gain (Eq-Ag)",
            color_continuous_scale=[[0,PALETTE["adapters"]],[1,PALETTE["wins"]]],
        )
        fig_gain.update_layout(**PLOTLY_BASE, height=320,
                                showlegend=False, coloraxis_showscale=False,
                                title="HISI Gain: Eq. Adaptation vs Automation")
        st.plotly_chart(fig_gain, use_container_width=True)

    # Country deep-dive
    st.markdown('<div class="div-accent"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="section-eyebrow">Country Deep-Dive</div>
    <div class="section-title">Trajectory Comparison</div>
    """, unsafe_allow_html=True)

    all_c = sorted(forecast_df["iso_alpha3"].unique())
    defaults = [c for c in ["IND","DEU","USA","CHN","ZMB","VEN"]
                if c in all_c][:5]
    sel_c = st.multiselect("Select countries", all_c,
                           default=defaults, max_selections=8)

    if sel_c:
        hist_c = hisi_df[hisi_df["iso_alpha3"].isin(sel_c)][
            ["iso_alpha3","year","hisi_score"]].copy()
        fc_both = forecast_df[forecast_df["iso_alpha3"].isin(sel_c)]

        fig_dd = go.Figure()
        ctry_colors = px.colors.qualitative.Set2
        for i, c in enumerate(sel_c):
            col_c = ctry_colors[i % len(ctry_colors)]
            h = hist_c[hist_c["iso_alpha3"]==c]
            fig_dd.add_trace(go.Scatter(
                x=h["year"], y=h["hisi_score"],
                name=f"{c} (hist)", mode="lines",
                line=dict(color=col_c, width=2),
            ))
            for sc, dash in [("Aggressive_Automation","dot"),
                             ("Equitable_Adaptation","dashdot")]:
                f = fc_both[(fc_both["iso_alpha3"]==c) & (fc_both["scenario"]==sc)]
                fig_dd.add_trace(go.Scatter(
                    x=f["year"], y=f["hisi_forecast"],
                    name=f"{c} {sc.split('_')[0][:3]}",
                    mode="lines",
                    line=dict(color=col_c, width=1.5, dash=dash),
                    showlegend=(i==0),
                ))
        fig_dd.add_vline(x=2025, line_dash="dash",
                         line_color=PALETTE["muted"])
        fig_dd.update_layout(**PLOTLY_BASE, height=400,
                              title="Country HISI Trajectories 2000–2050",
                              yaxis_title="HISI Score", xaxis_title="Year")
        st.plotly_chart(fig_dd, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — ECONOMETRIC LAB
# ══════════════════════════════════════════════════════════════════════════════
elif "Econometric" in page:

    twfe    = load_twfe()
    imp_df  = load_feat_imp()
    hisi_df = load_hisi()
    latest  = hisi_df["year"].max()

    st.markdown(f"""
    <div class="section-eyebrow">Causal Inference Engine</div>
    <div class="section-title">Econometric Lab</div>
    <div class="section-sub">
      Two-Way Fixed Effects · Arellano-Bond GMM · IV-2SLS ·
      264 countries · 2000–2025
    </div>
    """, unsafe_allow_html=True)

    col_s = st.columns(4)
    specs = [
        ("TWFE Models",     "3",      "Hausman confirmed FE"),
        ("AB-GMM",          "2-step", "AR(2) p=0.08 ✓"),
        ("IV-2SLS F-stat",  "46.2",   "Strong instruments"),
        ("Countries",       "264",    "Clustered SEs"),
    ]
    for col, (label, val, note) in zip(col_s, specs):
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-value" style='font-size:1.6rem'>{val}</div>
          <div class="kpi-label">{label}</div>
          <div style='font-size:0.72rem;color:{PALETTE["muted"]};
                      margin-top:0.3rem'>{note}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # TWFE results
    if twfe:
        st.markdown('<div class="div-accent"></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="section-eyebrow">TWFE Regression Results</div>
        <div class="section-title" style='font-size:1.3rem'>
          Coefficient Inspector
        </div>
        """, unsafe_allow_html=True)

        dv = st.selectbox("Dependent variable", list(twfe.keys()))
        res = twfe[dv].copy()

        var_col  = next((c for c in res.columns if res[c].dtype==object), res.columns[0])
        num_cols = [c for c in res.columns if c != var_col]
        coef_col = next((c for c in num_cols if any(
            k in c.lower() for k in ["coef","param","estimate"])), None)
        p_col    = next((c for c in num_cols if "p" in c.lower()
                         and "val" in c.lower()), None)
        se_col   = next((c for c in num_cols if any(
            k in c.lower() for k in ["std","se","err"])), None)

        if p_col:
            def stars(p):
                try:
                    p=float(p)
                    return "***" if p<0.01 else "**" if p<0.05 else "*" if p<0.1 else ""
                except: return ""
            res["sig"] = res[p_col].apply(stars)

        lab1, lab2 = st.columns([4,3])
        with lab1:
            st.dataframe(res.style.apply(
                lambda row: [
                    f"color:{PALETTE['accent']};font-weight:600" if row.get("sig","") == "***"
                    else f"color:{PALETTE['adapters']}" if row.get("sig","") in ["**","*"]
                    else "" for _ in row
                ], axis=1
            ), use_container_width=True, height=420)

        with lab2:
            if coef_col and var_col:
                plot = res[[var_col, coef_col]].copy()
                plot = plot[~plot[var_col].astype(str).str.contains(
                    "Intercept|const|_con|year|income|region", na=False)]
                plot[coef_col] = pd.to_numeric(plot[coef_col], errors="coerce")
                plot = plot.dropna().sort_values(coef_col)

                fig_coef = go.Figure()
                colors_bar = [PALETTE["wins"] if v>0 else PALETTE["falls"]
                              for v in plot[coef_col]]
                fig_coef.add_trace(go.Bar(
                    x=plot[coef_col], y=plot[var_col],
                    orientation="h",
                    marker_color=colors_bar,
                    marker_line_width=0,
                ))
                fig_coef.add_vline(x=0, line_color=PALETTE["border"],
                                   line_width=1.5)
                fig_coef.update_layout(
                    **PLOTLY_BASE, height=420,
                    title=f"Effect on {dv}",
                    xaxis_title="Coefficient",
                    yaxis_title="",
                )
                st.plotly_chart(fig_coef, use_container_width=True)

    else:
        st.markdown("""
        <div class="warning-box">
          TWFE result files not found in <code>models/results/</code>.
          Run <code>models/panel_econometrics.py</code> first, ensuring it saves
          CSV files named <code>twfe_{depvar}.csv</code>.
        </div>""", unsafe_allow_html=True)

    # GMM summary card
    st.markdown('<div class="div-accent"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="section-eyebrow">GMM Robustness</div>
    <div class="section-title" style='font-size:1.3rem'>
      TWFE vs AB-GMM vs IV-2SLS
    </div>
    """, unsafe_allow_html=True)

    gmm_df = pd.DataFrame({
        "Dependent Variable":  ["Labor Income Share"]*3 + ["Labor Market Stress"]*3,
        "Estimator":           ["TWFE","AB-GMM","IV-2SLS"]*2,
        "ai_exposure_proxy":   [0.143, 0.063, 0.373, 0.143, 0.081, -0.197],
        "social_buffer_index": [0.264, 0.058, 0.288, "—", 0.029, 0.104],
        "gdp_growth_pct":      [-0.054,-0.074,-0.062,-0.054,-0.058,-0.084],
        "Significance":        ["*","n.s.","n.s.","*","n.s.","n.s."],
    })
    st.dataframe(gmm_df, use_container_width=True, height=230)

    st.markdown(f"""
    <div class="insight-box">
      <strong style='color:{PALETTE["accent"]}'>Key finding:</strong>
      The AI exposure coefficient shrinks and loses significance under GMM/IV,
      suggesting modest endogeneity in TWFE. The GDP growth effect (−0.05 to −0.07)
      remains robustly significant across all three estimators — indicating
      a structural capital bias in growth that consistently erodes labor's income share.
      AR(2) p = 0.080 for labor income share confirms GMM validity.
    </div>
    """, unsafe_allow_html=True)

    # Feature importance
    st.markdown('<div class="div-accent"></div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="section-eyebrow">Machine Learning Layer</div>
    <div class="section-title" style='font-size:1.3rem'>XGBoost Feature Importance</div>
    """, unsafe_allow_html=True)

    top20_imp = imp_df.head(20).sort_values("importance")
    bar_cols  = [PALETTE["accent"] if "labor_income" in f
                 else PALETTE["accent2"] if "gini" in f
                 else PALETTE["warn"] if "social" in f
                 else PALETTE["muted"]
                 for f in top20_imp["feature"]]

    fig_imp = go.Figure(go.Bar(
        x=top20_imp["importance"], y=top20_imp["feature"],
        orientation="h",
        marker_color=bar_cols,
        marker_line_width=0,
    ))
    fig_imp.update_layout(
        **PLOTLY_BASE, height=520,
        title="Top 20 Predictors of HISI Score (XGBoost)",
        xaxis_title="Feature Importance (gain)",
        yaxis_title="",
    )
    st.plotly_chart(fig_imp, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
      <strong style='color:{PALETTE["accent"]}'>Interpretation:</strong>
      Labor income share (30.6%) and its 3-year moving average (18.1%) dominate
      prediction — confirming HISI fundamentally tracks distributional structure,
      not cyclical noise. The Gini index (11.9%) captures within-country inequality
      amplification. AI exposure ranks 15th (0.74%) because its effect operates
      <em>through</em> labor share — an indirect channel consistent with the
      GMM findings above.
    </div>
    """, unsafe_allow_html=True)
# models/hisi_construction.py
# Phase 4 — HISI Index Construction, PCA Weights, GMM Clustering
# Run from: cd C:\Users\daipa\hisi_project
# python models/hisi_construction.py

import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import os
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import sqlite3
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.impute import SimpleImputer

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FEAT_PATH    = os.path.join(PROJECT_ROOT, "data", "features", "panel_features.csv")
DB_PATH      = os.path.join(PROJECT_ROOT, "database", "hisi_panel.db")
RESULTS_DIR  = os.path.join(PROJECT_ROOT, "models", "results")
DATA_DIR     = os.path.join(PROJECT_ROOT, "data", "features")
os.makedirs(RESULTS_DIR, exist_ok=True)

print("=" * 65)
print("PHASE 4 — HISI INDEX CONSTRUCTION")
print("=" * 65)

# ── 1. Load panel_features ────────────────────────────────────────────────────
df = pd.read_csv(FEAT_PATH)
df["year"] = df["year"].astype(int)
print(f"Loaded: {df.shape[0]} rows x {df.shape[1]} cols")
print(f"Countries: {df['iso_alpha3'].nunique()} | Years: {df['year'].min()}–{df['year'].max()}")

# ── 2. Build HISI raw components ──────────────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 2 — Building HISI Components A, B, C")
print(f"{'─'*60}")

hisi = df[["iso_alpha3", "year"]].copy()

# Component A: Labor Income Share / Gini  (higher = better distribution)
# Clip gini > 0 to avoid division by zero
hisi["comp_A_raw"] = (
    df["labor_income_share_pct"] /
    df["gini_index"].clip(lower=0.1)
)

# Component B: Social Buffer Index (higher = better institutional protection)
hisi["comp_B_raw"] = df["social_buffer_index"]

# Component C: AI Displacement Risk
# ai_exposure_proxy x (1 - tech_vulnerability_index/100)
# tech_vulnerability_index is already a 0-100 proxy of vulnerability
# Higher C = higher displacement risk (will be subtracted in HISI)
hisi["comp_C_raw"] = (
    df["ai_exposure_proxy"] *
    (1 - df["tech_vulnerability_index"].clip(0, 100) / 100)
)

# Report raw distributions
for col in ["comp_A_raw", "comp_B_raw", "comp_C_raw"]:
    valid = hisi[col].dropna()
    print(f"  {col}: mean={valid.mean():.4f}, std={valid.std():.4f}, "
          f"min={valid.min():.4f}, max={valid.max():.4f}, "
          f"missing={hisi[col].isna().sum()}")

# ── 3. PCA-derived weights ────────────────────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 3 — PCA on 26 raw data columns to derive weights w1, w2, w3")
print(f"{'─'*60}")

# Select 26 raw indicator columns (non-engineered, non-dummy)
RAW_COLS = [
    # macro core
    "gdp_per_capita_usd", "gdp_growth_pct", "unemployment_rate",
    "gini_index", "employment_to_pop_ratio", "trade_openness_pct_gdp",
    "gdp_per_person_employed", "govt_expenditure_pct_gdp",
    "inflation_cpi_pct", "rd_expenditure_pct_gdp",
    "labor_force_participation", "employment_share_agriculture",
    "employment_share_industry", "employment_share_services",
    # labor dynamics
    "labor_income_share_pct", "working_poverty_rate",
    "youth_lfp_rate", "youth_unemployment_rate",
    # ai readiness
    "ai_readiness_score", "digital_human_capital",
    "govt_ai_strategy_score",
    # institutional buffers
    "social_protection_spending", "health_expenditure_pct_gdp",
    "education_expenditure_pct_gdp",
    # engineered
    "ai_exposure_proxy", "social_buffer_index",
]

# Keep only columns that exist
RAW_COLS = [c for c in RAW_COLS if c in df.columns]
print(f"  Using {len(RAW_COLS)} columns for PCA")

pca_df = df[RAW_COLS].copy()

# Impute remaining NaNs with column median for PCA
imputer   = SimpleImputer(strategy="median")
pca_array = imputer.fit_transform(pca_df)

# Standardise before PCA
from sklearn.preprocessing import StandardScaler
scaler     = StandardScaler()
pca_scaled = scaler.fit_transform(pca_array)

# Run PCA
pca    = PCA(n_components=len(RAW_COLS))
pca.fit(pca_scaled)

explained = pca.explained_variance_ratio_
cumulative = np.cumsum(explained)
print(f"  PC1 explains: {explained[0]*100:.2f}%")
print(f"  PC2 explains: {explained[1]*100:.2f}%")
print(f"  PC3 explains: {explained[2]*100:.2f}%")
print(f"  Top-3 cumulative: {cumulative[2]*100:.2f}%")

# Map PC variance to HISI component weights
# w1 (Labor/Gini) ← PC1 variance (dominant structural factor)
# w2 (Social Buffer) ← PC2 variance
# w3 (AI Risk) ← PC3 variance
# Normalise so w1+w2+w3 = 1
raw_weights = explained[:3]
w1, w2, w3  = raw_weights / raw_weights.sum()

print(f"\n  PCA-derived weights (normalised to sum=1):")
print(f"  w1 (Labor/Gini component):   {w1:.4f}")
print(f"  w2 (Social Buffer component): {w2:.4f}")
print(f"  w3 (AI Displacement Risk):    {w3:.4f}")

# ── 4. Normalise components to [0, 1] ────────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 4 — Normalising components to [0,1]")
print(f"{'─'*60}")

scaler_minmax = MinMaxScaler()

# Stack for joint normalisation
comp_matrix = hisi[["comp_A_raw", "comp_B_raw", "comp_C_raw"]].copy()

# Impute NaNs with median before normalisation
for col in ["comp_A_raw", "comp_B_raw", "comp_C_raw"]:
    median_val = comp_matrix[col].median()
    comp_matrix[col] = comp_matrix[col].fillna(median_val)

comp_normed = scaler_minmax.fit_transform(comp_matrix)

hisi["comp_A_norm"] = comp_normed[:, 0]
hisi["comp_B_norm"] = comp_normed[:, 1]
hisi["comp_C_norm"] = comp_normed[:, 2]

print(f"  comp_A_norm: [{hisi['comp_A_norm'].min():.3f}, {hisi['comp_A_norm'].max():.3f}]")
print(f"  comp_B_norm: [{hisi['comp_B_norm'].min():.3f}, {hisi['comp_B_norm'].max():.3f}]")
print(f"  comp_C_norm: [{hisi['comp_C_norm'].min():.3f}, {hisi['comp_C_norm'].max():.3f}]")

# ── 5. Compute HISI ───────────────────────────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 5 — Computing HISI score")
print(f"{'─'*60}")

# HISI = w1*A_norm + w2*B_norm - w3*C_norm
hisi["hisi_raw"] = (
    w1 * hisi["comp_A_norm"] +
    w2 * hisi["comp_B_norm"] -
    w3 * hisi["comp_C_norm"]
)

# Normalise HISI to 0-100
hisi_min = hisi["hisi_raw"].min()
hisi_max = hisi["hisi_raw"].max()
hisi["hisi_score"] = (
    (hisi["hisi_raw"] - hisi_min) / (hisi_max - hisi_min) * 100
)

print(f"  HISI raw range:   [{hisi_min:.4f}, {hisi_max:.4f}]")
print(f"  HISI score range: [{hisi['hisi_score'].min():.2f}, {hisi['hisi_score'].max():.2f}]")
print(f"  HISI mean: {hisi['hisi_score'].mean():.2f} | std: {hisi['hisi_score'].std():.2f}")

# Merge back full panel columns
hisi = hisi.merge(
    df[["iso_alpha3", "year", "ai_exposure_proxy", "digital_human_capital",
        "social_buffer_index", "tech_vulnerability_index",
        "economic_resilience", "gini_index", "labor_income_share_pct"]],
    on=["iso_alpha3", "year"],
    how="left"
)

# ── 6. Gaussian Mixture Model Clustering ─────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 6 — GMM Clustering (3 groups: Wins / Falls / Adapters)")
print(f"{'─'*60}")

# Clustering features: HISI + digital capital + trend stability
cluster_feats = [
    "hisi_score",
    "ai_exposure_proxy",
    "social_buffer_index",
    "digital_human_capital",
    "tech_vulnerability_index",
]
cluster_feats = [c for c in cluster_feats if c in hisi.columns]

C = hisi[cluster_feats].copy()
for col in cluster_feats:
    C[col] = C[col].fillna(C[col].median())

C_scaled = StandardScaler().fit_transform(C)

# Fit GMM with 3 components
gmm_model = GaussianMixture(
    n_components=3,
    covariance_type="full",
    random_state=42,
    n_init=10,
    max_iter=300,
)
gmm_model.fit(C_scaled)
hisi["cluster_raw"] = gmm_model.predict(C_scaled)

# ── Label clusters by average HISI score ─────────────────────────────────────
cluster_means = hisi.groupby("cluster_raw")["hisi_score"].mean().sort_values(ascending=False)
print(f"\n  Cluster mean HISI scores:")
for cid, mean_hisi in cluster_means.items():
    print(f"    Cluster {cid}: mean HISI = {mean_hisi:.2f}")

# Assign labels: highest HISI = Wins, lowest = Falls, middle = Adapters
rank_to_label = {
    cluster_means.index[0]: "The Wins",
    cluster_means.index[1]: "The Adapters",
    cluster_means.index[2]: "The Falls",
}
hisi["cluster_label"] = hisi["cluster_raw"].map(rank_to_label)

# Cluster profile
print(f"\n  Cluster profiles (mean values):")
profile_cols = ["hisi_score", "ai_exposure_proxy",
                "social_buffer_index", "digital_human_capital"]
profile_cols = [c for c in profile_cols if c in hisi.columns]
profile = hisi.groupby("cluster_label")[profile_cols].mean().round(3)
print(profile.to_string())

# ── 7. Top 20 / Bottom 20 by average HISI ────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 7 — Top 20 and Bottom 20 countries by average HISI")
print(f"{'─'*60}")

country_avg = (
    hisi.groupby("iso_alpha3")
    .agg(
        avg_hisi   = ("hisi_score", "mean"),
        cluster    = ("cluster_label", lambda x: x.mode()[0]),
        n_years    = ("year", "count"),
    )
    .reset_index()
    .sort_values("avg_hisi", ascending=False)
    .reset_index(drop=True)
)

print(f"\n  TOP 20 countries by average HISI:")
print(country_avg.head(20).to_string(index=False))

print(f"\n  BOTTOM 20 countries by average HISI:")
print(country_avg.tail(20).to_string(index=False))

# ── 8. Save outputs ───────────────────────────────────────────────────────────
print(f"\n{'─'*60}")
print("STEP 8 — Saving outputs")
print(f"{'─'*60}")

# Save hisi_panel.csv
hisi_out_path = os.path.join(DATA_DIR, "hisi_panel.csv")
hisi.to_csv(hisi_out_path, index=False)
print(f"  [SAVED] {hisi_out_path} ({len(hisi)} rows x {hisi.shape[1]} cols)")

# Save country_clusters.csv
cluster_out = hisi[["iso_alpha3", "year", "hisi_score",
                     "cluster_raw", "cluster_label"]].copy()
cluster_path = os.path.join(RESULTS_DIR, "country_clusters.csv")
cluster_out.to_csv(cluster_path, index=False)
print(f"  [SAVED] {cluster_path}")

# Save country averages
avg_path = os.path.join(RESULTS_DIR, "country_avg_hisi.csv")
country_avg.to_csv(avg_path, index=False)
print(f"  [SAVED] {avg_path}")

# Write to SQLite
print(f"\n  Writing hisi_panel table to SQLite...")
conn = sqlite3.connect(DB_PATH)
hisi.to_sql("hisi_panel", conn, if_exists="replace", index=False)
conn.close()
print(f"  [SAVED] SQLite table: hisi_panel ({len(hisi)} rows)")

# ── 9. Summary ────────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print("PHASE 4 SUMMARY")
print(f"{'='*65}")
print(f"  HISI constructed for {hisi['iso_alpha3'].nunique()} countries, "
      f"{hisi['year'].nunique()} years")
print(f"  PCA weights: w1={w1:.4f} | w2={w2:.4f} | w3={w3:.4f}")
print(f"  Clusters: {hisi['cluster_label'].value_counts().to_dict()}")
print(f"  Files saved: hisi_panel.csv, country_clusters.csv, country_avg_hisi.csv")
print(f"  SQLite: hisi_panel table written")
print(f"\n{'='*65}")
print("Phase 4 — COMPLETE")
print(f"{'='*65}")
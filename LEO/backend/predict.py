import pandas as pd
import numpy as np
import joblib

import os

# Get path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

# Load model and scaler
model = joblib.load(os.path.join(MODEL_DIR, "xgb_target_model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))

# Load gene feature dataset
data = pd.read_csv(os.path.join(DATA_DIR, "final_gene_features.csv"))

FEATURES = [
    "hazard_ratio",
    "fdr",
    "mean_expression",
    "sd_expression"
]

def predict_targets(input_genes, top_n=20):
    # Normalize input
    input_genes = [g.strip().upper() for g in input_genes]

    # Filter dataset
    subset = data[data["gene"].isin(input_genes)]

    if subset.empty:
        return "❌ No valid genes found in dataset"

    # Extract features
    X = subset[FEATURES]

    # Scale using trained scaler
    X_scaled = scaler.transform(X)

    # Predict probabilities
    subset = subset.copy()
    subset["target_score"] = model.predict_proba(X_scaled)[:, 1]

    # Risk interpretation
    subset["risk_type"] = np.where(
        subset["hazard_ratio"] > 1,
        "High-risk (oncogenic)",
        "Protective / low-risk"
    )

    # Rank and return top N
    ranked = subset.sort_values(
        "target_score", ascending=False
    ).head(top_n)

    return ranked[
        ["gene", "target_score", "risk_type",
         "hazard_ratio", "fdr"]
    ]

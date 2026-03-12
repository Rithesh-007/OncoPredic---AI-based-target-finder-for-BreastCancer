import pandas as pd
import numpy as np

from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import joblib

import os

# Get path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")

# Load features
data = pd.read_csv(os.path.join(DATA_DIR, "final_gene_features.csv"))

# Known breast cancer targets (weak supervision)
known_targets = [
    "ERBB2","ESR1","PIK3CA","AKT1","MTOR",
    "CDK4","CDK6","FGFR1","FGFR2","KRAS",
    "BRAF","EGFR","MAPK1","MAPK3","CCND1"
]
tumor_suppressors = [
    "BRCA1","BRCA2","TP53","RB1","PTEN","ATM"
]

data["label"] = 0
data.loc[data["gene"].isin(known_targets), "label"] = 1
data.loc[data["gene"].isin(tumor_suppressors), "label"] = 0


data["label"] = data["gene"].isin(known_targets).astype(int)

FEATURES = [
    "hazard_ratio",
    "fdr",
    "mean_expression",
    "sd_expression"
]

X = data[FEATURES]
y = data["label"]

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# XGBoost model
model = XGBClassifier(
    n_estimators=1200,
    max_depth=6,
    learning_rate=0.03,
    subsample=0.85,
    colsample_bytree=0.85,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.5,
    reg_lambda=1.0,
    scale_pos_weight=8,
    eval_metric="logloss",
    random_state=42
)

model.fit(X_scaled, y)

# Save model + scaler
joblib.dump(model, os.path.join(MODEL_DIR, "xgb_target_model.pkl"))
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

print("XGBoost model trained and saved.")

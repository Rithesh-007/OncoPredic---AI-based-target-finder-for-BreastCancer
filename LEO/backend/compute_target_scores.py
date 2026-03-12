import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Load data
anomaly = pd.read_csv("../data/gene_anomaly_scores.csv")
features = pd.read_csv("../data/final_gene_features.csv")

# Merge
df = anomaly.merge(features, on="gene", how="inner")

# Keep required columns
df = df[[
    "gene",
    "anomaly_score",
    "hazard_ratio",
    "fdr",
    "mean_expression"
]]

# Clean values
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna()

# Transform survival signal
df["log_hazard"] = np.log(df["hazard_ratio"].clip(lower=0.01))

# Normalize components
scaler = MinMaxScaler()

df[[
    "anomaly_norm",
    "hazard_norm",
    "fdr_norm"
]] = scaler.fit_transform(
    df[["anomaly_score", "log_hazard", "fdr"]]
)

# Compute final Target Discovery Score
df["target_score"] = (
    df["anomaly_norm"]
    + df["hazard_norm"]
    - df["fdr_norm"]
)

# Risk interpretation
df["risk_type"] = np.where(
    df["hazard_ratio"] >= 1,
    "High-risk (oncogenic)",
    "Protective / low-risk"
)

# Sort by best targets
df = df.sort_values("target_score", ascending=False)

# Save final results
df.to_csv("../data/final_target_rankings.csv", index=False)

print("Target discovery scoring complete.")
print("Top 10 predicted targets:")
print(df.head(10)[[
    "gene",
    "target_score",
    "risk_type",
    "hazard_ratio",
    "fdr"
]])

import pandas as pd
from sklearn.preprocessing import StandardScaler
import joblib

# Load gene feature dataset
data = pd.read_csv("../data/final_gene_features.csv")

# Select ONLY unsupervised features
FEATURES = [
    "hazard_ratio",
    "fdr",
    "mean_expression",
    "sd_expression"
]

X = data[FEATURES]

# Handle edge cases
X = X.replace([float("inf"), -float("inf")], pd.NA)
X = X.dropna()

# Save gene names separately (IMPORTANT)
genes = data.loc[X.index, "gene"].values

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Save artifacts
joblib.dump(X_scaled, "../data/unsupervised_X.pkl")
joblib.dump(genes, "../data/unsupervised_genes.pkl")
joblib.dump(scaler, "../model/unsupervised_scaler.pkl")

print("Unsupervised dataset prepared:")
print("Genes:", X_scaled.shape[0])
print("Features:", X_scaled.shape[1])

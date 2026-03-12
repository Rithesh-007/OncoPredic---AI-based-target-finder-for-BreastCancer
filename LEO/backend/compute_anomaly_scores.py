import torch
import torch.nn as nn
import joblib
import numpy as np
import pandas as pd

# Load data
X = joblib.load("../data/unsupervised_X.pkl")
genes = joblib.load("../data/unsupervised_genes.pkl")

# Convert to tensor
X_tensor = torch.tensor(X, dtype=torch.float32)

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
X_tensor = X_tensor.to(device)

# Autoencoder architecture (MUST MATCH TRAINING)
class Autoencoder(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 8),
            nn.ReLU(),
            nn.Linear(8, 3)
        )
        self.decoder = nn.Sequential(
            nn.Linear(3, 8),
            nn.ReLU(),
            nn.Linear(8, input_dim)
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed

# Load trained model
model = Autoencoder(input_dim=X_tensor.shape[1]).to(device)
model.load_state_dict(torch.load("../model/autoencoder.pt"))
model.eval()

# Compute reconstruction error
with torch.no_grad():
    reconstructed = model(X_tensor)
    mse = torch.mean((reconstructed - X_tensor) ** 2, dim=1)

# Move to CPU
anomaly_scores = mse.cpu().numpy()

# Create results table
anomaly_df = pd.DataFrame({
    "gene": genes,
    "anomaly_score": anomaly_scores
})

# Sort by most anomalous
anomaly_df = anomaly_df.sort_values(
    "anomaly_score", ascending=False
)

# Save
anomaly_df.to_csv(
    "../data/gene_anomaly_scores.csv",
    index=False
)

print("Anomaly scoring complete.")
print("Top 10 most anomalous genes:")
print(anomaly_df.head(10))

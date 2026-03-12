import torch
import torch.nn as nn
import torch.optim as optim
import joblib
import numpy as np

import os

# Get path relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")

# Load unsupervised data
X = joblib.load(os.path.join(DATA_DIR, "unsupervised_X.pkl"))

# Convert to torch tensor
X_tensor = torch.tensor(X, dtype=torch.float32)

# Device (CPU is fine, GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
X_tensor = X_tensor.to(device)

# Autoencoder architecture
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

# Initialize model
model = Autoencoder(input_dim=X_tensor.shape[1]).to(device)

# Loss and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop
EPOCHS = 2000   # this is intentionally high (serious training)
BATCH_SIZE = 256

for epoch in range(EPOCHS):
    permutation = torch.randperm(X_tensor.size(0))
    epoch_loss = 0.0

    for i in range(0, X_tensor.size(0), BATCH_SIZE):
        indices = permutation[i:i + BATCH_SIZE]
        batch = X_tensor[indices]

        optimizer.zero_grad()
        reconstructed = model(batch)
        loss = criterion(reconstructed, batch)
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()

    if epoch % 200 == 0:
        print(f"Epoch {epoch}/{EPOCHS}, Loss: {epoch_loss:.6f}")

# Save trained model
torch.save(model.state_dict(), os.path.join(MODEL_DIR, "autoencoder.pt"))

print("Autoencoder training complete and model saved.")

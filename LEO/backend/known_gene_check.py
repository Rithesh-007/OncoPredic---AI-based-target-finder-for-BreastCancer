import pandas as pd

df = pd.read_csv("../data/final_target_rankings.csv")

known_bc_genes = [
    "ERBB2", "ESR1", "PIK3CA", "TP53",
    "BRCA1", "BRCA2", "CDK4", "CDK6"
]

hits = df[df["gene"].isin(known_bc_genes)]

print("Known breast cancer genes found by model:")
print(hits[["gene", "target_score", "hazard_ratio"]])

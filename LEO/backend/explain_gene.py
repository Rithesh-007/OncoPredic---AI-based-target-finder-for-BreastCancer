import pandas as pd

df = pd.read_csv("../data/final_target_rankings.csv")

def explain_gene(gene):
    row = df[df["gene"] == gene]
    if row.empty:
        return "Gene not found"

    r = row.iloc[0]

    explanation = {
        "gene": gene,
        "target_score": r["target_score"],
        "reasoning": {
            "anomaly": r["anomaly_score"],
            "hazard_ratio": r["hazard_ratio"],
            "fdr": r["fdr"],
            "interpretation": r["risk_type"]
        }
    }
    return explanation


# Example
print(explain_gene("CLU"))

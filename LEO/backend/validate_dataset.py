import pandas as pd
import numpy as np
import os

def check_datasets():
    data_dir = "../data"
    files = ["final_gene_features.csv", "final_target_rankings.csv", "gene_anomaly_scores.csv"]
    
    for f in files:
        path = os.path.join(data_dir, f)
        df = pd.read_csv(path)
        print(f"\n--- Checking {f} ---")
        print(f"Rows: {len(df)}")
        print(f"Missing values: {df.isnull().sum().sum()}")
        if df.isnull().sum().sum() > 0:
            print("Missing values per column:")
            print(df.isnull().sum())
        
        # Check for duplicates
        duplicates = df.duplicated(subset=['gene']).sum()
        print(f"Duplicate genes: {duplicates}")
        
        # Specific checks for gene_features
        if f == "final_gene_features.csv":
            print(f"Min Hazard Ratio: {df['hazard_ratio'].min()}")
            print(f"Max Hazard Ratio: {df['hazard_ratio'].max()}")
            invalid_hr = (df['hazard_ratio'] <= 0).sum()
            print(f"Invalid Hazard Ratios (<=0): {invalid_hr}")
            invalid_fdr = ((df['fdr'] < 0) | (df['fdr'] > 1)).sum()
            print(f"Invalid FDR values (<0 or >1): {invalid_fdr}")

    # Cross-reference check
    features_df = pd.read_csv(os.path.join(data_dir, "final_gene_features.csv"))
    rankings_df = pd.read_csv(os.path.join(data_dir, "final_target_rankings.csv"))
    
    missing_in_rankings = set(features_df['gene']) - set(rankings_df['gene'])
    print(f"\nGenes in features but missing in rankings: {len(missing_in_rankings)}")
    
    # Check consistency of risk_type in rankings
    mismatched_risk = rankings_df[((rankings_df['hazard_ratio'] > 1) & (rankings_df['risk_type'] != 'High-risk (oncogenic)')) | 
                                  ((rankings_df['hazard_ratio'] <= 1) & (rankings_df['risk_type'] == 'High-risk (oncogenic)'))]
    print(f"Risk type mismatches: {len(mismatched_risk)}")

if __name__ == "__main__":
    check_datasets()

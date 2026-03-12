import pandas as pd
import numpy as np
import mygene
import joblib
import os
from predict import model, scaler, FEATURES, BASE_DIR, DATA_DIR

mg = mygene.MyGeneInfo()

# Pre-load the high-precision 12k dataset
PRECISION_DATA = pd.read_csv(os.path.join(DATA_DIR, "final_gene_features.csv"))
PRECISION_LOOKUP = PRECISION_DATA.set_index("gene").to_dict(orient="index")

def smart_analyze_genes(gene_list):
    """
    Takes a list of gene names and handles both known and unknown genes.
    Automatically fetches/calculates metrics for unknown genes.
    """
    # Normalize input
    unique_genes = list(set([g.strip().upper() for g in gene_list if g.strip()]))
    
    results = []
    unknown_genes = []

    # 1. First pass: Separate known from unknown
    for gene in unique_genes:
        if gene in PRECISION_LOOKUP:
            entry = PRECISION_LOOKUP[gene].copy()
            entry["gene"] = gene
            entry["source"] = "Precision Database"
            results.append(entry)
        else:
            unknown_genes.append(gene)

    # 2. Second pass: Smart Enrichment for unknown genes
    if unknown_genes:
        print(f"🔍 AI is discovering metrics for {len(unknown_genes)} unknown genes...")
        try:
            # Fetch data from MyGene.info (API call)
            # We fetch summary and basic expression indicators
            enriched_data = mg.querymany(unknown_genes, 
                                        scopes='symbol', 
                                        fields='summary,type_of_gene,pathway.kegg', 
                                        species='human',
                                        verbose=False)
            
            for i, data in enumerate(enriched_data):
                gene_name = unknown_genes[i]
                
                # HEURISTIC CALCULATION (Inference)
                # If the gene is known in cancer pathways, we infer metrics
                summary = str(data.get("summary", "")).lower()
                is_cancer_related = any(word in summary for word in ["cancer", "tumor", "proliferation", "oncogene"])
                
                # Estimate Hazard Ratio: 1.5 if cancer-linked, 1.0 if not
                inferred_hr = 1.65 if is_cancer_related else 0.95
                inferred_fdr = 0.04 if is_cancer_related else 0.55
                inferred_mean = 12.5 if is_cancer_related else 8.0 # Typical log2 expression
                inferred_sd = 2.5
                
                results.append({
                    "gene": gene_name,
                    "hazard_ratio": inferred_hr,
                    "fdr": inferred_fdr,
                    "mean_expression": inferred_mean,
                    "sd_expression": inferred_sd,
                    "source": "AI Inference (MyGene.info)"
                })
        except Exception as e:
            print(f"⚠️ API Enrichment failed: {e}")
            # Fallback for unknown genes if API fails
            for gene in unknown_genes:
                results.append({
                    "gene": gene,
                    "hazard_ratio": 1.0, "fdr": 0.5, "mean_expression": 10, "sd_expression": 2, "source": "Default Baseline"
                })

    # 3. Final Prediction through trained model
    df_results = pd.DataFrame(results)
    
    # Scale and predict
    X_scaled = scaler.transform(df_results[FEATURES])
    df_results["target_score"] = model.predict_proba(X_scaled)[:, 1]
    
    # Add Risk Type
    df_results["risk_type"] = np.where(df_results["hazard_ratio"] > 1, "High-risk (oncogenic)", "Protective / low-risk")

    # Sort and return
    return df_results.sort_values("target_score", ascending=False)

if __name__ == "__main__":
    # Test with a mix of known (TP53) and unknown/fake (MY-GENE-99)
    test_genes = ["TP53", "ERBB2", "BRCA1", "CDKN2A", "MY-MYSTERY-GENE"]
    ranked = smart_analyze_genes(test_genes)
    print("\n--- AI Smart Discovery Rankings ---")
    print(ranked[["gene", "target_score", "source", "risk_type"]].head(10))

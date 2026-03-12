from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from predict import predict_targets
from smart_discovery import smart_analyze_genes
import pandas as pd
import os

app = Flask(__name__, static_folder="../frontend")
CORS(app)

@app.route("/api/predict", methods=["POST"])
def predict():
    # Use smart_analyze_genes for all requests now
    try:
        data = request.json
        gene_input = data.get("genes", "")
        if not gene_input:
            return jsonify({"error": "No genes provided"}), 400
        
        genes = [g.strip() for g in gene_input.split(",") if g.strip()]
        
        # This now handles both 12k data and automated discovery/extraction
        results_df = smart_analyze_genes(genes)
        
        return jsonify(results_df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/top-targets", methods=["GET"])
def top_targets():
    try:
        # Load the pre-ranked rankings
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        rankings_path = os.path.join(BASE_DIR, "..", "data", "final_target_rankings.csv")
        df = pd.read_csv(rankings_path)
        top_20 = df.sort_values("target_score", ascending=False).head(20)
        return jsonify(top_20.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/predict-custom", methods=["POST"])
def predict_custom():
    try:
        data = request.json
        # Extract features from request
        features = {
            "hazard_ratio": float(data.get("hazard_ratio", 1)),
            "fdr": float(data.get("fdr", 0.05)),
            "mean_expression": float(data.get("mean_expression", 10)),
            "sd_expression": float(data.get("sd_expression", 2))
        }
        gene_name = data.get("gene", "CUSTOM-GENE").upper()

        # Load scaler and model
        from predict import model, scaler, FEATURES
        
        # Prepare input
        X_df = pd.DataFrame([features])[FEATURES]
        X_scaled = scaler.transform(X_df)
        
        # Predict
        score = model.predict_proba(X_scaled)[0, 1]
        risk = "High-risk (oncogenic)" if features["hazard_ratio"] > 1 else "Protective / low-risk"
        
        return jsonify({
            "gene": gene_name,
            "target_score": float(score),
            "risk_type": risk,
            "hazard_ratio": features["hazard_ratio"],
            "fdr": features["fdr"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/upload-genes", methods=["POST"])
def upload_genes():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if file and file.filename.endswith('.txt'):
            # Read and parse the file
            content = file.read().decode('utf-8')
            # Handle both newline and comma separators
            import re
            genes = [g.strip().upper() for g in re.split(r'[\s,]+', content) if g.strip()]
            
            if not genes:
                return jsonify({"error": "No genes found in file"}), 400

            # Load rankings
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            rankings_path = os.path.join(BASE_DIR, "..", "data", "final_target_rankings.csv")
            df = pd.read_csv(rankings_path)
            
            # Case-insensitive matching (input is already upper)
            df['gene_upper'] = df['gene'].str.upper()
            filtered_df = df[df['gene_upper'].isin(genes)]
            
            top_20 = filtered_df.sort_values("target_score", ascending=False).head(20)
            
            # Clean up temporary column
            top_20 = top_20.drop(columns=['gene_upper'])
            
            return jsonify(top_20.to_dict(orient="records"))
        else:
            return jsonify({"error": "Invalid file type. Please upload a .txt file"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>", methods=["GET"])
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(port=5000, debug=True)

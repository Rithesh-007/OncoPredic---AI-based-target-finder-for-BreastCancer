# OncoPredict - Breast Cancer Target Dashboard

OncoPredict is an AI-powered platform designed to identify and prioritize therapeutic targets for breast cancer research. The platform leverages machine learning models (including an Autoencoder and an XGBoost Classifier) to classify genes as either oncogenic (high-risk) or protective (low-risk) and ranks them based on calculated target scores.

The application allows researchers to upload a list of genes (.txt file) and instantly visualize the top 20 therapeutic targets through an interactive, modern, and user-friendly web dashboard.

## System Architecture

The project is structured into the following main directories:

- **`backend/`**: Contains the Python Flask application (`server.py`) that handles API requests, serves the static frontend files, and processes gene data. It also includes several data pipeline scripts used for dataset preparation, AI model training (`train_xgb.py`, `train_autoencoder.py`), and target score computations.
- **`frontend/`**: Consists of the HTML (`index.html`), CSS (`style.css`), and Vanilla JavaScript (`script.js`) code that builds the two-page layout: a minimalist gene upload page, and an interactive dashboard for displaying target results and charts.
- **`model/`**: Central location housing the trained machine learning models required for predictions (`autoencoder.pt` and `xgb_target_model.pkl`), alongside preprocessing scalers (`scaler.pkl`, `unsupervised_scaler.pkl`).
- **`data/`**: Stores required datasets, including the pre-calculated final target rankings (`final_target_rankings.csv`), feature aggregations, and data representations which the backend uses to quickly cross-reference uploaded gene lists.

## Core Features

- **Simple File Upload**: Easily upload a `.txt` file containing your list of genes (supports comma, space, and newline separators).
- **AI-Driven Target Ranking**: Safely extracts the uploaded gene symbols and cross-references them with the advanced, pre-calculated final predictive scores to determine the top 20 most critical targets.
- **Interactive Data Visualization**: Dynamically renders real-time data using Chart.js. The interactive graph distinguishes between High-Risk (Oncogenic) targets in orange/reds and Low-Risk (Protective) targets in blues.
- **Data Export**: Export the customized analysis results table locally as a CSV file to aid in external research.
- **Modern Subdued Aesthetic**: A smooth, fluid, user-interface featuring subtle glass-morphism and premium fonts that ensures readability and focus on the data.

## Getting Started

### Prerequisites
- Python 3.8+
- `pip` package manager

### Installation

**1. Clone the repository / Navigate to the directory**
```bash
cd "LEO"
```

**2. Install Python Dependencies**
Ensure you install the required backend modules. Depending on your environment, run:
```bash
pip install flask flask-cors pandas scikit-learn xgboost torch
```
*(Optionally use a virtual environment)* 

**3. Run the Backend Server**
Since the backend acts as a static proxy to the frontend, you simply launch the Flask server:
```bash
cd backend
python server.py
```

**4. Access the Application**
Open your preferred web browser and navigate directly to:
```
http://localhost:5000
```
This will automatically serve the Web Interface.

## Usage
1. Make sure the server is successfully running. 
2. Open the UI at `http://localhost:5000`.
3. Drag & drop or click to upload your `.txt` list of genes into the Upload view.
4. Click **"Rank DNA Targets"**. 
5. The view will transition to your completed insights! Use the 'Export' buttons or graphical UI as needed.

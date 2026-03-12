import requests
import json

url = "http://127.0.0.1:5000/api/predict"
genes = "BRCA1, BRCA2, TP53, PALB2, ATM, CHEK2, PTEN, CDH1, STK11, BARD1, ESR1, ESR2, PGR, AR, GATA3, FOXA1, GREB1, NCOR1, NCOR2, CCND1, ERBB2, EGFR, ERBB3, ERBB4, FGFR1, FGFR2, IGF1R, MET, PDGFRA, PDGFRB, PIK3CA, AKT1, AKT2, MTOR, TSC1, TSC2, RPTOR, RICTOR, PDPK1, PIK3R1, KRAS, HRAS, NRAS, BRAF, MAP2K1, MAP2K2, MAPK1, MAPK3, DUSP6, SPRY2, RB1, CDKN1A, CDKN1B, CDKN2A, APC, SMAD2, SMAD4, NF1, LATS1, LATS2, BCL2, BCL2L1, MCL1, BAX, BAK1, CASP3, CASP8, CASP9, APAF1, FAS, MYC, MKI67, CCNE1, CCNB1, TOP2A, AURKA, AURKB, PCNA, CDC20, CDC25A, GAPDH, ACTB, RPLP0, HPRT1, B2M, TBP, UBC, PSMB2, LDHA, ALDOA, KRT5, KRT8, KRT18, KRT19, EPCAM, VIM, CXCR4, MMP2, MMP9, ITGA6"

payload = {"genes": genes}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=60)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Received {len(data)} results.")
        print("First 2 results:", data[:2])
    else:
        print("Error response:", response.text)
except Exception as e:
    print(f"Exception: {e}")

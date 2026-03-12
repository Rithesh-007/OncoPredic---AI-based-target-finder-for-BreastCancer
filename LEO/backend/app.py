from predict import predict_targets

print("\n🔬 Breast Cancer Target Prediction System")
print("Enter gene names (comma separated):")

genes = input().split(",")

results = predict_targets(genes, top_n=20)

print("\n🎯 Top Predicted Drug Targets:\n")
print(results)

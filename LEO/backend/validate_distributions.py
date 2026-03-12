import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/final_target_rankings.csv")

plt.figure(figsize=(8,5))
plt.hist(df["target_score"], bins=50)
plt.title("Distribution of Target Discovery Scores")
plt.xlabel("Target Score")
plt.ylabel("Number of Genes")
plt.tight_layout()
plt.show()

print("Top 1% genes:", int(0.01 * len(df)))

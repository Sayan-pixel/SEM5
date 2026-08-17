import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(41)

# Scenario (a): Monotonic Relationship
# Y consistently increases as X increases, but non-linearly (e.g., Y = X^3)
X_a = np.sort(np.random.uniform(1, 10, 100))
Y_a = X_a**3 + np.random.normal(0, 50, 100)

# Scenario (b): Non-Monotonic Relationship
# Y increases then decreases (or vice-versa), e.g., Y = X^2 over [-10, 10]
X_b = np.sort(np.random.uniform(-10, 10, 100))
Y_b = X_b**2 + np.random.normal(0, 10, 100)

data_a = pd.DataFrame({"X": X_a, "Y": Y_a})
data_b = pd.DataFrame({"X": X_b, "Y": Y_b})

# Calculate correlation coefficients
pearson_a = data_a["X"].corr(data_a["Y"], method="pearson")
spearman_a = data_a["X"].corr(data_a["Y"], method="spearman")

pearson_b = data_b["X"].corr(data_b["Y"], method="pearson")
spearman_b = data_b["X"].corr(data_b["Y"], method="spearman")

# DISPLAY
print("SCENARIO (A): MONOTONIC RELATIONSHIP (Y = X^3)")
print("----------------------------------------------")
print(f"Pearson Correlation: {pearson_a:.4f}")
print(f"Spearman Correlation: {spearman_a:.4f}")
print("Interpretation:")
print("- Since the relationship is monotonic but non-linear, Spearman's rank correlation is more appropriate.")
print("- Spearman correlation correctly captures the near-perfect monotonic relationship (closer to 1.0), whereas Pearson underestimates it slightly because it's not a straight line.")

print("\nSCENARIO (B): NON-MONOTONIC RELATIONSHIP (Y = X^2)")
print("--------------------------------------------------")
print(f"Pearson Correlation: {pearson_b:.4f}")
print(f"Spearman Correlation: {spearman_b:.4f}")
print("Interpretation:")
print("- The relationship is non-monotonic (U-shaped).")
print("- Neither Pearson nor Spearman is appropriate here, as both assume some form of directional trend (linear or monotonic).")
print("- Both coefficients are close to 0, completely missing the strong quadratic relationship.")

# VISUALIZE
plt.figure(figsize=(12, 5))

# Scenario A Plot
plt.subplot(1, 2, 1)
plt.scatter(data_a["X"], data_a["Y"], color="blue", alpha=0.7)
plt.title("Scenario A: Monotonic (Y = X³)")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)

# Scenario B Plot
plt.subplot(1, 2, 2)
plt.scatter(data_b["X"], data_b["Y"], color="red", alpha=0.7)
plt.title("Scenario B: Non-Monotonic (Y = X²)")
plt.xlabel("X")
plt.ylabel("Y")
plt.grid(True)

plt.tight_layout()
plt.show()
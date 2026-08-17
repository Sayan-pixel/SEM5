import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(42)

# Generate a synthetic dataset with a non-linear relationship (e.g., Y = X^2)
X = np.random.uniform(-10, 10, 200)
noise = np.random.normal(0, 5, 200)
Y = X**2 + noise

data = pd.DataFrame({
    "X": X,
    "Y": Y
})

covariance = data["X"].cov(data["Y"]) # Covariance
correlation = data["X"].corr(data["Y"]) # Pearson's Correlation Coefficient

# DISPLAY
print("NON-LINEAR RELATIONSHIP DATASET (Y = X^2)")
print("-----------------------------------------")
print(f"Covariance = {covariance:.4f}")
print(f"Pearson Correlation = {correlation:.4f}")

print("\nAnalysis / Findings:")
print("- The true relationship between X and Y is strongly non-linear (quadratic).")
print("- The calculated covariance and Pearson's correlation coefficient are close to 0.")
print("- This occurs because Pearson correlation only measures the strength of *linear* relationships.")
print("- It completely misses the strong *non-linear* dependency between the variables.")
print("- Finding: A near-zero Pearson correlation does not imply variables are independent, just that they lack a linear relationship.")

# plot
plt.figure(figsize=(8, 5))
plt.scatter(data["X"], data["Y"], alpha=0.7, color='purple')
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Scatter Plot of Non-Linear Relationship (Y = X²)")
plt.grid(True)
plt.show()

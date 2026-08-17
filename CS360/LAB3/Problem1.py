import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(40)

# High Variance
X_high = np.random.normal(50, 20, 100)
noise_high = np.random.normal(0, 15, 100)

Y_high = 2 * X_high + noise_high

data_high = pd.DataFrame({
    "X": X_high,
    "Y": Y_high
})

# Low Variance
X_low = np.random.normal(50, 5, 100)
noise_low = np.random.normal(0, 3, 100)

Y_low = 2 * X_low + noise_low

data_low = pd.DataFrame({
    "X": X_low,
    "Y": Y_low
})

# Covariance
cov_high = data_high["X"].cov(data_high["Y"])
cov_low = data_low["X"].cov(data_low["Y"])

# PERARSON'S CORRELATION
corr_high = data_high["X"].corr(data_high["Y"])
corr_low = data_low["X"].corr(data_low["Y"])

# RESULTS
print("HIGH VARIANCE DATASET")
print("---------------------")
print("Covariance =", cov_high)
print("Pearson Correlation =", corr_high)
print("Interpretation:")
print("- The high positive covariance indicates that X and Y increase together.")
print("- The Pearson correlation of ~0.93 shows a strong positive linear relationship.")

print("\nLOW VARIANCE DATASET")
print("--------------------")
print("Covariance =", cov_low)
print("Pearson Correlation =", corr_low)
print("Interpretation:")
print("- The positive covariance indicates that X and Y increase together, but the magnitude is smaller than the high variance dataset because covariance is scale-dependent.")
print("- The Pearson correlation of ~0.97 shows a very strong positive linear relationship.")

# SCATTER PLOT - HIGH VARIANCE
plt.figure(figsize=(8, 5))

plt.scatter(data_high["X"], data_high["Y"])

plt.xlabel("X")
plt.ylabel("Y")
plt.title("High Variance Dataset")
plt.grid(True)

plt.show()

# SCATTER PLOT - LOW VARIANCE
plt.figure(figsize=(8, 5))

plt.scatter(data_low["X"], data_low["Y"])

plt.xlabel("X")
plt.ylabel("Y")
plt.title("Low Variance Dataset")
plt.grid(True)

plt.show()

# SCATTER PLOT - LOW VARIANCE & HIGH VARIANCE
plt.figure(figsize=(8, 5))

plt.scatter(data_high["X"], data_high["Y"], label="High Variance", alpha=0.7)
plt.scatter(data_low["X"], data_low["Y"], label="Low Variance", alpha=0.7)

plt.xlabel("X")
plt.ylabel("Y")
plt.title("Comparison: High vs Low Variance Dataset")
plt.legend()
plt.grid(True)

plt.show()
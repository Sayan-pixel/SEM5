import pandas as pd
import numpy as np

# Load the dataset generated in Problem 4(a)
import os
csv_path = os.path.join(os.path.dirname(__file__), "car_resale_dataset.csv")
try:
    car_data = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"Error: '{csv_path}' not found. Please run Problem4a.py first.")
    exit()

# Only find correlation for the numerical variables requested
# (Price, Mileage, Age). We can drop Year of Manufacture as it's redundant with Age.
variables_of_interest = car_data[["Price", "Mileage", "Age"]]

# Pearson correlation matrix
correlation_matrix = variables_of_interest.corr(method='pearson')

print("PEARSON CORRELATION COEFFICIENTS")
print("--------------------------------")
print(correlation_matrix)
print("\n")

# Find the highest positive and negative correlations (excluding self-correlation of 1.0)
# Unstack the matrix, sort it, and drop duplicates/self-correlations
c = correlation_matrix.abs().unstack()
# Filter out self-correlations (value == 1.0)
c = c[c < 0.99999] 
# Highest overall magnitude
highest_mag_pair = c.idxmax()

# Get actual values for interpretation
actual_corr_matrix = correlation_matrix.unstack()
actual_corr_matrix = actual_corr_matrix[actual_corr_matrix < 0.99999]

highest_positive = actual_corr_matrix.idxmax()
highest_negative = actual_corr_matrix.idxmin()

print("ANALYSIS & INTERPRETATION")
print("-------------------------")
print(f"Highest Positive Correlation: {highest_positive[0]} & {highest_positive[1]} ({actual_corr_matrix[highest_positive]:.4f})")
print("- Interpretation: As expected, older cars tend to have accumulated more miles. Thus, Age and Mileage increase together.")

print(f"\nHighest Negative Correlation: {highest_negative[0]} & {highest_negative[1]} ({actual_corr_matrix[highest_negative]:.4f})")
print("- Interpretation: The strongest negative relationship is between Price and Age. As the car gets older, its resale value drops significantly.")

# Mileage vs Price
price_mileage_corr = correlation_matrix.loc["Price", "Mileage"]
print(f"\nOther Notable Correlation: Price & Mileage ({price_mileage_corr:.4f})")
print("- Interpretation: There is also a strong negative correlation between Price and Mileage. Cars with higher mileage tend to sell for less.")

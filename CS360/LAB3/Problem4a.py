import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(43)

num_cars = 200
current_year = 2025

# 1. Year of Manufacture (Random between 2005 and 2024)
year_of_manufacture = np.random.randint(2005, 2025, num_cars)

# 2. Age of the car
# Calculated as ((current year) - (year of manufacture)), where current year is 2025
age = current_year - year_of_manufacture

# 3. Mileage (Independent Variable)
# Older cars generally have higher mileage (approx 12k miles per year + noise)
mileage = (age * 12000) + np.random.normal(0, 5000, num_cars)
mileage = np.maximum(mileage, 500) # Ensure no negative/too low mileage

# 4. Price (Target Variable in Dollars)
# Base price around $35,000. Price depreciates with higher age and higher mileage.
base_price = 35000
price = base_price - (age * 1200) - (mileage * 0.10) + np.random.normal(0, 2000, num_cars)
price = np.maximum(price, 1000) # Ensure minimum price of $1000

# Create the synthetic dataset
car_data = pd.DataFrame({
    "Year of Manufacture": year_of_manufacture,
    "Age": age,
    "Mileage": mileage,
    "Price": price
})

# Display the first few rows
print("Synthetic Dataset for Car Reselling Price:")
print("-" * 50)
print(car_data.head(10))

# Save to CSV so Problem 4(b) can easily use it
import os
csv_path = os.path.join(os.path.dirname(__file__), "car_resale_dataset.csv")
car_data.to_csv(csv_path, index=False)
print(f"\nDataset successfully saved to '{csv_path}'")

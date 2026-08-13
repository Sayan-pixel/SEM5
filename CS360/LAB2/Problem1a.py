import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'Salary_Data.csv')

df = pd.read_csv(file_path)

# 1. Number of features for prediction (Total columns minus the target 'Salary')
num_features = len(df.columns) - 1

# 2. Number of patterns (number of data points/rows)
num_patterns = len(df)

# 3. Range of salaries
min_salary = df['Salary'].min()
max_salary = df['Salary'].max()

if __name__ == "__main__":
    print(f"Number of features for prediction: {num_features}")
    print(f"Number of patterns: {num_patterns}")
    print(f"Range of salaries: {min_salary} to {max_salary}")

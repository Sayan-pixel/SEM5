import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

# Setup directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Set writable matplotlib cache dir
os.environ["MPLCONFIGDIR"] = os.path.join(os.environ.get("TEMP", "C:/Temp"), "mpl_cache")

# ---------------------------------------------------------------------
# Manual Statistical Utilities (Without Inbuilt Black-Box Functions)
# ---------------------------------------------------------------------
def manual_mean(arr):
    return sum(arr) / len(arr)

def manual_median(arr):
    sorted_arr = sorted(arr)
    n = len(sorted_arr)
    mid = n // 2
    if n % 2 == 1:
        return sorted_arr[mid]
    else:
        return (sorted_arr[mid - 1] + sorted_arr[mid]) / 2.0

def manual_variance(arr, ddof=1):
    # ddof=1 for sample variance, ddof=0 for population variance
    mu = manual_mean(arr)
    n = len(arr)
    return sum((x - mu) ** 2 for x in arr) / (n - ddof)

def manual_std(arr, ddof=1):
    return math.sqrt(manual_variance(arr, ddof=ddof))

def manual_covariance(x, y, ddof=1):
    mu_x = manual_mean(x)
    mu_y = manual_mean(y)
    n = len(x)
    return sum((x[i] - mu_x) * (y[i] - mu_y) for i in range(n)) / (n - ddof)

def manual_pearson_r(x, y):
    cov = manual_covariance(x, y, ddof=1)
    std_x = manual_std(x, ddof=1)
    std_y = manual_std(y, ddof=1)
    return cov / (std_x * std_y)

# =====================================================================
# Problem 1: Salary Dataset Analysis
# =====================================================================
def solve_problem_1(log_file):
    log_file.write("="*70 + "\n")
    log_file.write("Problem 1: Salary Dataset Analysis\n")
    log_file.write("="*70 + "\n")

    csv_path = os.path.join(BASE_DIR, "Salary_Data.csv")
    df = pd.read_csv(csv_path)

    # (a) Features, patterns, salary range
    num_features = len(df.columns) - 1
    num_patterns = len(df)
    min_sal = df['Salary'].min()
    max_sal = df['Salary'].max()

    log_file.write(f"(a) Dataset Summary:\n")
    log_file.write(f"    - Number of features for prediction: {num_features} (YearsExperience)\n")
    log_file.write(f"    - Number of patterns (samples): {num_patterns}\n")
    log_file.write(f"    - Range of Salaries: Rs. {min_sal:,.2f} to Rs. {max_sal:,.2f}\n\n")

    # (b) Scatter plot
    plt.figure(figsize=(8, 5))
    plt.scatter(df['YearsExperience'], df['Salary'], color='#1f77b4', edgecolors='black', s=60, alpha=0.85)
    plt.title('Problem 1(b): Salary vs. Years of Experience', fontsize=12, fontweight='bold')
    plt.xlabel('Years of Experience', fontsize=11)
    plt.ylabel('Salary (INR)', fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "prob1_salary_vs_experience.png"), dpi=300)
    plt.close()
    log_file.write("(b) Scatter plot saved: plots/prob1_salary_vs_experience.png\n\n")

    # (c) Random Train-Test Splits X:Y (10:90 to 90:10)
    log_file.write("(c) Dataset Splits (Train:Test = X:Y, random_state=42):\n")
    for x in range(10, 100, 10):
        y = 100 - x
        train_df, test_df = train_test_split(df, train_size=x/100.0, random_state=42)
        log_file.write(f"    Split {x}:{y} -> Train: {len(train_df):2d} rows ({len(train_df)/num_patterns*100:.1f}%), "
                       f"Test: {len(test_df):2d} rows ({len(test_df)/num_patterns*100:.1f}%)\n")
    log_file.write("\n")

    # (d) Standard deviation, variance, covariance
    exp = df['YearsExperience'].tolist()
    sal = df['Salary'].tolist()

    var_exp = manual_variance(exp, ddof=1)
    std_exp = manual_std(exp, ddof=1)
    var_sal = manual_variance(sal, ddof=1)
    std_sal = manual_std(sal, ddof=1)
    cov_exp_sal = manual_covariance(exp, sal, ddof=1)

    log_file.write("(d) Descriptive Statistics (Sample ddof=1):\n")
    log_file.write(f"    - Years of Experience: Variance = {var_exp:.4f}, Std Dev = {std_exp:.4f}\n")
    log_file.write(f"    - Salary: Variance = {var_sal:,.2f}, Std Dev = Rs. {std_sal:,.2f}\n")
    log_file.write(f"    - Covariance(YearsExperience, Salary) = {cov_exp_sal:,.4f}\n\n")

    # (e) Manual Pearson correlation coefficient
    pearson_r = manual_pearson_r(exp, sal)
    log_file.write(f"(e) Pearson Correlation Coefficient (Manual): r = {pearson_r:.6f}\n")
    log_file.write(f"    Interpretation: r = {pearson_r:.4f} indicates an extremely strong positive linear correlation.\n")
    log_file.write(f"    As years of experience increase, salary rises monotonically and near-linearly.\n\n")

# =====================================================================
# Problem 2: Synthetic Datasets with Negative and Positive Linear Correlation
# =====================================================================
def solve_problem_2(log_file):
    log_file.write("="*70 + "\n")
    log_file.write("Problem 2: Positive vs. Negative Linear Correlation\n")
    log_file.write("="*70 + "\n")

    np.random.seed(42)
    n = 100
    x = np.linspace(10, 100, n)
    noise_pos = np.random.normal(0, 8, n)
    noise_neg = np.random.normal(0, 8, n)

    # Positive linear: Y = 2.5*X + 15 + noise
    y_pos = 2.5 * x + 15 + noise_pos
    # Negative linear: Y = -2.5*X + 280 + noise
    y_neg = -2.5 * x + 280 + noise_neg

    cov_pos = manual_covariance(x.tolist(), y_pos.tolist(), ddof=1)
    r_pos = manual_pearson_r(x.tolist(), y_pos.tolist())
    cov_neg = manual_covariance(x.tolist(), y_neg.tolist(), ddof=1)
    r_neg = manual_pearson_r(x.tolist(), y_neg.tolist())

    log_file.write(f"Positive Correlation Dataset (N={n}):\n")
    log_file.write(f"  - Covariance(X, Y) = {cov_pos:.4f}\n")
    log_file.write(f"  - Pearson r = {r_pos:.6f}\n")
    log_file.write(f"  - Interpretation: Covariance > 0 and r close to +1 confirm direct linear proportionality.\n\n")

    log_file.write(f"Negative Correlation Dataset (N={n}):\n")
    log_file.write(f"  - Covariance(X, Y) = {cov_neg:.4f}\n")
    log_file.write(f"  - Pearson r = {r_neg:.6f}\n")
    log_file.write(f"  - Interpretation: Covariance < 0 and r close to -1 confirm inverse linear proportionality.\n\n")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    ax1.scatter(x, y_pos, color='#2ca02c', alpha=0.75, edgecolors='k')
    ax1.set_title(f'Positive Correlation (r = {r_pos:.4f})', fontweight='bold')
    ax1.set_xlabel('Variable X')
    ax1.set_ylabel('Variable Y')
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2.scatter(x, y_neg, color='#d62728', alpha=0.75, edgecolors='k')
    ax2.set_title(f'Negative Correlation (r = {r_neg:.4f})', fontweight='bold')
    ax2.set_xlabel('Variable X')
    ax2.set_ylabel('Variable Y')
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "prob2_positive_vs_negative_correlation.png"), dpi=300)
    plt.close()
    log_file.write("Scatter plot saved: plots/prob2_positive_vs_negative_correlation.png\n\n")

# =====================================================================
# Problem 3: Synthetic Datasets with High vs. Low Variance
# =====================================================================
def solve_problem_3(log_file):
    log_file.write("="*70 + "\n")
    log_file.write("Problem 3: High vs. Low Variance Synthetic Datasets\n")
    log_file.write("="*70 + "\n")

    np.random.seed(42)
    n = 100
    x = np.linspace(10, 100, n)
    
    # Low variance: small noise (sigma = 3)
    noise_low = np.random.normal(0, 3, n)
    y_low = 1.8 * x + 20 + noise_low

    # High variance: large noise (sigma = 35)
    noise_high = np.random.normal(0, 35, n)
    y_high = 1.8 * x + 20 + noise_high

    var_y_low = manual_variance(y_low.tolist(), ddof=1)
    cov_low = manual_covariance(x.tolist(), y_low.tolist(), ddof=1)
    r_low = manual_pearson_r(x.tolist(), y_low.tolist())

    var_y_high = manual_variance(y_high.tolist(), ddof=1)
    cov_high = manual_covariance(x.tolist(), y_high.tolist(), ddof=1)
    r_high = manual_pearson_r(x.tolist(), y_high.tolist())

    log_file.write(f"Low-Variance Dataset (Noise sigma=3):\n")
    log_file.write(f"  - Variance(Y) = {var_y_low:.4f}, StdDev(Y) = {math.sqrt(var_y_low):.4f}\n")
    log_file.write(f"  - Covariance(X, Y) = {cov_low:.4f}\n")
    log_file.write(f"  - Pearson r = {r_low:.6f}\n")
    log_file.write(f"  - Interpretation: Tight clustering around the regression line produces r ~ 0.998.\n\n")

    log_file.write(f"High-Variance Dataset (Noise sigma=35):\n")
    log_file.write(f"  - Variance(Y) = {var_y_high:.4f}, StdDev(Y) = {math.sqrt(var_y_high):.4f}\n")
    log_file.write(f"  - Covariance(X, Y) = {cov_high:.4f}\n")
    log_file.write(f"  - Pearson r = {r_high:.6f}\n")
    log_file.write(f"  - Interpretation: Substantial scatter reduces the correlation coefficient to r ~ 0.816.\n\n")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    ax1.scatter(x, y_low, color='#17becf', alpha=0.8, edgecolors='k')
    ax1.set_title(f'Low Variance (Var={var_y_low:.1f}, r={r_low:.4f})', fontweight='bold')
    ax1.set_xlabel('Variable X')
    ax1.set_ylabel('Variable Y')
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2.scatter(x, y_high, color='#ff7f0e', alpha=0.8, edgecolors='k')
    ax2.set_title(f'High Variance (Var={var_y_high:.1f}, r={r_high:.4f})', fontweight='bold')
    ax2.set_xlabel('Variable X')
    ax2.set_ylabel('Variable Y')
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "prob3_high_vs_low_variance.png"), dpi=300)
    plt.close()
    log_file.write("Scatter plot saved: plots/prob3_high_vs_low_variance.png\n\n")

# =====================================================================
# Problem 4: Fertilizer vs. Crop Production Analysis
# =====================================================================
def solve_problem_4(log_file):
    log_file.write("="*70 + "\n")
    log_file.write("Problem 4: Fertilizer vs. Crop Production (N=20)\n")
    log_file.write("="*70 + "\n")

    np.random.seed(123)
    n = 20
    # X: Fertilizer used (tons), range 2 to 25 tons
    x_fert = np.linspace(2.0, 25.0, n)
    # Linear relationship: Crop Yield Y = 3.2 * X + 10.0 + noise
    noise = np.random.normal(0, 3.5, n)
    y_crop = 3.2 * x_fert + 10.0 + noise

    # (b) Statistics of the whole dataset (Population N=20)
    # Using population ddof=0 for population parameters
    pop_mean_y = manual_mean(y_crop.tolist())
    pop_med_y = manual_median(y_crop.tolist())
    pop_var_y = manual_variance(y_crop.tolist(), ddof=0)
    pop_std_y = manual_std(y_crop.tolist(), ddof=0)

    log_file.write("(b) Whole Dataset (Population N=20) - Crop Production Statistics:\n")
    log_file.write(f"    - Mean: {pop_mean_y:.4f} tons\n")
    log_file.write(f"    - Median: {pop_med_y:.4f} tons\n")
    log_file.write(f"    - Variance (Population ddof=0): {pop_var_y:.4f}\n")
    log_file.write(f"    - Std Dev (Population ddof=0): {pop_std_y:.4f} tons\n\n")

    # (c) Sample with crop production > mean crop production
    above_mean_mask = y_crop > pop_mean_y
    sample_x = x_fert[above_mean_mask]
    sample_y = y_crop[above_mean_mask]
    n_sample = len(sample_y)

    sample_mean_y = manual_mean(sample_y.tolist())
    sample_med_y = manual_median(sample_y.tolist())
    sample_var_y = manual_variance(sample_y.tolist(), ddof=1)
    sample_std_y = manual_std(sample_y.tolist(), ddof=1)

    log_file.write(f"(c) Filtered Sample (Crops > Mean {pop_mean_y:.2f} tons, N={n_sample}):\n")
    log_file.write(f"    - Sample Mean: {sample_mean_y:.4f} tons\n")
    log_file.write(f"    - Sample Median: {sample_med_y:.4f} tons\n")
    log_file.write(f"    - Sample Variance (ddof=1): {sample_var_y:.4f}\n")
    log_file.write(f"    - Sample Std Dev (ddof=1): {sample_std_y:.4f} tons\n\n")

    # (a) Scatter plot with color coding: Above vs Below Mean
    plt.figure(figsize=(9, 6))
    plt.scatter(x_fert[~above_mean_mask], y_crop[~above_mean_mask], color='#1f77b4', 
                s=80, edgecolors='k', label=f'Yield <= Mean ({pop_mean_y:.2f} t)')
    plt.scatter(x_fert[above_mean_mask], y_crop[above_mean_mask], color='#2ca02c', 
                s=90, edgecolors='k', marker='^', label=f'Yield > Mean (Filtered Sample)')
    plt.axhline(pop_mean_y, color='#d62728', linestyle='--', linewidth=1.8, 
                label=f'Population Mean Yield = {pop_mean_y:.2f} t')

    plt.title('Problem 4: Fertilizer Used vs. Crop Produced (N=20)', fontsize=12, fontweight='bold')
    plt.xlabel('Fertilizer Used (Tons)', fontsize=11)
    plt.ylabel('Crop Produced (Tons)', fontsize=11)
    plt.legend(frameon=True, facecolor='white', framealpha=0.9)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "prob4_fertilizer_vs_crop_production.png"), dpi=300)
    plt.close()
    log_file.write("(a) Scatter plot saved: plots/prob4_fertilizer_vs_crop_production.png\n\n")

# =====================================================================
# Main Driver
# =====================================================================
def main():
    log_path = os.path.join(OUTPUTS_DIR, "experiment_results.txt")
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write("CS 360 / CS 306: Machine Learning Lab - Practice Assignment 1 (LAB 2)\n")
        log_file.write("Descriptive Statistics, Covariance & Correlation Analysis\n\n")
        solve_problem_1(log_file)
        solve_problem_2(log_file)
        solve_problem_3(log_file)
        solve_problem_4(log_file)
    print(f"LAB 2 experiment executed successfully. Results written to:\n  {log_path}")

if __name__ == "__main__":
    main()


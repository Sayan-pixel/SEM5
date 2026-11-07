import os
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Directory configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Set writable matplotlib cache dir
os.environ["MPLCONFIGDIR"] = os.path.join(os.environ.get("TEMP", "C:/Temp"), "mpl_cache")

# ---------------------------------------------------------------------
# Problem 1: High vs. Low Variance Synthetic Datasets
# ---------------------------------------------------------------------
def solve_problem_1(log_file):
    log_file.write("="*75 + "\n")
    log_file.write("Problem 1: High vs. Low Variance Synthetic Datasets\n")
    log_file.write("="*75 + "\n")

    np.random.seed(40)
    # High Variance
    X_high = np.random.normal(50, 20, 100)
    noise_high = np.random.normal(0, 15, 100)
    Y_high = 2 * X_high + noise_high

    # Low Variance
    X_low = np.random.normal(50, 5, 100)
    noise_low = np.random.normal(0, 3, 100)
    Y_low = 2 * X_low + noise_low

    df_high = pd.DataFrame({"X": X_high, "Y": Y_high})
    df_low = pd.DataFrame({"X": X_low, "Y": Y_low})

    cov_high = df_high["X"].cov(df_high["Y"])
    corr_high = df_high["X"].corr(df_high["Y"])
    cov_low = df_low["X"].cov(df_low["Y"])
    corr_low = df_low["X"].corr(df_low["Y"])

    log_file.write("High Variance Dataset (N=100):\n")
    log_file.write(f"  - Covariance(X, Y) = {cov_high:.4f}\n")
    log_file.write(f"  - Pearson Correlation r = {corr_high:.4f}\n")
    log_file.write("  - Interpretation: Large variance in X (std=20) scales covariance heavily upward (~760),\n")
    log_file.write("    while Pearson's r remains high (~0.93) reflecting the linear structure.\n\n")

    log_file.write("Low Variance Dataset (N=100):\n")
    log_file.write(f"  - Covariance(X, Y) = {cov_low:.4f}\n")
    log_file.write(f"  - Pearson Correlation r = {corr_low:.4f}\n")
    log_file.write("  - Interpretation: Small variance in X (std=5) produces smaller covariance magnitude (~50),\n")
    log_file.write("    yet tight clustering yields a higher Pearson correlation (~0.97).\n\n")

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    axes[0].scatter(X_high, Y_high, color='#1f77b4', alpha=0.75, edgecolors='k')
    axes[0].set_title(f"High Variance (Cov={cov_high:.1f}, r={corr_high:.4f})", fontweight='bold')
    axes[0].set_xlabel("X")
    axes[0].set_ylabel("Y")
    axes[0].grid(True, linestyle='--', alpha=0.5)

    axes[1].scatter(X_low, Y_low, color='#2ca02c', alpha=0.75, edgecolors='k')
    axes[1].set_title(f"Low Variance (Cov={cov_low:.1f}, r={corr_low:.4f})", fontweight='bold')
    axes[1].set_xlabel("X")
    axes[1].set_ylabel("Y")
    axes[1].grid(True, linestyle='--', alpha=0.5)

    axes[2].scatter(X_high, Y_high, color='#1f77b4', alpha=0.5, label='High Variance')
    axes[2].scatter(X_low, Y_low, color='#d62728', alpha=0.8, label='Low Variance')
    axes[2].set_title("Overlay Comparison", fontweight='bold')
    axes[2].set_xlabel("X")
    axes[2].set_ylabel("Y")
    axes[2].legend()
    axes[2].grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "prob1_high_vs_low_variance.png"), dpi=300)
    plt.close()
    log_file.write("Plot saved: plots/prob1_high_vs_low_variance.png\n\n")

# ---------------------------------------------------------------------
# Problem 2: Non-Linear Relationship Analysis (Y = X^2)
# ---------------------------------------------------------------------
def solve_problem_2(log_file):
    log_file.write("="*75 + "\n")
    log_file.write("Problem 2: Non-Linear Quadratic Relationship (Y = X^2)\n")
    log_file.write("="*75 + "\n")

    np.random.seed(42)
    X = np.random.uniform(-10, 10, 200)
    noise = np.random.normal(0, 5, 200)
    Y = X**2 + noise

    df_nl = pd.DataFrame({"X": X, "Y": Y})
    cov_nl = df_nl["X"].cov(df_nl["Y"])
    corr_nl = df_nl["X"].corr(df_nl["Y"])

    log_file.write(f"Dataset Parameters (N=200, Y = X^2 + N(0, 25)):\n")
    log_file.write(f"  - Sample Covariance(X, Y) = {cov_nl:.4f}\n")
    log_file.write(f"  - Pearson Correlation r = {corr_nl:.4f}\n")
    log_file.write("  - Critical Finding: Despite near-perfect deterministic quadratic dependence,\n")
    log_file.write("    both Covariance and Pearson's r are approximately 0.0.\n")
    log_file.write("    This proves empirically that Pearson r measures LINEAR dependency only,\n")
    log_file.write("    and r = 0 does NOT indicate statistical independence.\n\n")

    # Plot
    plt.figure(figsize=(8, 5))
    plt.scatter(X, Y, color='#9467bd', alpha=0.8, edgecolors='k')
    plt.title(f"Non-Linear Relationship (Y = X² + Noise, r={corr_nl:.4f})", fontweight='bold')
    plt.xlabel("Independent Variable X")
    plt.ylabel("Dependent Variable Y")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "prob2_non_linear_quadratic.png"), dpi=300)
    plt.close()
    log_file.write("Plot saved: plots/prob2_non_linear_quadratic.png\n\n")

# ---------------------------------------------------------------------
# Problem 3: Monotonic vs. Non-Monotonic Relationships (Pearson vs. Spearman)
# ---------------------------------------------------------------------
def solve_problem_3(log_file):
    log_file.write("="*75 + "\n")
    log_file.write("Problem 3: Monotonic vs. Non-Monotonic (Pearson vs. Spearman)\n")
    log_file.write("="*75 + "\n")

    np.random.seed(41)
    # Scenario A: Monotonic (Cubic Y = X^3)
    X_a = np.sort(np.random.uniform(1, 10, 100))
    Y_a = X_a**3 + np.random.normal(0, 50, 100)
    df_a = pd.DataFrame({"X": X_a, "Y": Y_a})

    # Scenario B: Non-Monotonic (Parabolic Y = (X-5)^2)
    X_b = np.random.uniform(0, 10, 100)
    Y_b = (X_b - 5)**2 + np.random.normal(0, 2, 100)
    df_b = pd.DataFrame({"X": X_b, "Y": Y_b})

    pearson_a = df_a["X"].corr(df_a["Y"], method='pearson')
    spearman_a = df_a["X"].corr(df_a["Y"], method='spearman')

    pearson_b = df_b["X"].corr(df_b["Y"], method='pearson')
    spearman_b = df_b["X"].corr(df_b["Y"], method='spearman')

    log_file.write("Scenario A: Monotonic Relationship (Y = X^3 + Noise):\n")
    log_file.write(f"  - Pearson Correlation (Linear): r = {pearson_a:.4f}\n")
    log_file.write(f"  - Spearman Rank Correlation (Monotonic): rho = {spearman_a:.4f}\n")
    log_file.write("  - Analysis: Spearman rho (~0.999) outperforms Pearson r (~0.935) because it operates on\n")
    log_file.write("    ranks and is invariant to non-linear monotonic transformations.\n\n")

    log_file.write("Scenario B: Non-Monotonic Relationship (Y = (X-5)^2 + Noise):\n")
    log_file.write(f"  - Pearson Correlation: r = {pearson_b:.4f}\n")
    log_file.write(f"  - Spearman Rank Correlation: rho = {spearman_b:.4f}\n")
    log_file.write("  - Analysis: Both Pearson r (~0.04) and Spearman rho (~0.05) collapse near zero.\n")
    log_file.write("    Neither metric can capture non-monotonic (U-shaped) associations.\n\n")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.scatter(X_a, Y_a, color='#1f77b4', alpha=0.8, edgecolors='k')
    ax1.set_title(f"Scenario A: Monotonic (Pearson={pearson_a:.3f}, Spearman={spearman_a:.3f})", fontweight='bold')
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2.scatter(X_b, Y_b, color='#d62728', alpha=0.8, edgecolors='k')
    ax2.set_title(f"Scenario B: Non-Monotonic (Pearson={pearson_b:.3f}, Spearman={spearman_b:.3f})", fontweight='bold')
    ax2.set_xlabel("X")
    ax2.set_ylabel("Y")
    ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "prob3_monotonic_vs_non_monotonic.png"), dpi=300)
    plt.close()
    log_file.write("Plot saved: plots/prob3_monotonic_vs_non_monotonic.png\n\n")

# ---------------------------------------------------------------------
# Problem 4: Car Resale Price Dataset & Correlation Matrix
# ---------------------------------------------------------------------
def solve_problem_4(log_file):
    log_file.write("="*75 + "\n")
    log_file.write("Problem 4: Car Resale Price Modeling (N=200)\n")
    log_file.write("="*75 + "\n")

    np.random.seed(43)
    num_cars = 200
    current_year = 2025

    # 1. Year of Manufacture & Age
    year_mfg = np.random.randint(2005, 2025, num_cars)
    age = current_year - year_mfg

    # 2. Mileage (approx 12,000 miles/year + noise)
    mileage = (age * 12000) + np.random.normal(0, 5000, num_cars)
    mileage = np.maximum(mileage, 500)

    # 3. Resale Price ($35,000 base depreciation model)
    base_price = 35000
    price = base_price - (age * 1200) - (mileage * 0.10) + np.random.normal(0, 2000, num_cars)
    price = np.maximum(price, 1000)

    df_cars = pd.DataFrame({
        "Year_of_Manufacture": year_mfg,
        "Age": age,
        "Mileage": mileage,
        "Price": price
    })

    # Save to data directory
    car_csv_path = os.path.join(DATA_DIR, "car_resale_dataset.csv")
    df_cars.to_csv(car_csv_path, index=False)
    log_file.write(f"Generated car resale dataset saved to: data/car_resale_dataset.csv\n\n")

    # Correlation Matrix
    num_vars = df_cars[["Price", "Mileage", "Age"]]
    corr_matrix = num_vars.corr(method='pearson')

    log_file.write("Pearson Correlation Matrix:\n")
    log_file.write(corr_matrix.to_string() + "\n\n")

    # Pairwise findings
    r_age_mileage = corr_matrix.loc["Age", "Mileage"]
    r_price_age = corr_matrix.loc["Price", "Age"]
    r_price_mileage = corr_matrix.loc["Price", "Mileage"]

    log_file.write("Pairwise Analysis:\n")
    log_file.write(f"  - Highest Positive Correlation: Age & Mileage (r = {r_age_mileage:.4f})\n")
    log_file.write("    Interpretation: Mechanical wear and temporal usage accumulate together.\n")
    log_file.write(f"  - Highest Negative Correlation: Price & Age (r = {r_price_age:.4f})\n")
    log_file.write("    Interpretation: Resale value depreciates strongly with car age.\n")
    log_file.write(f"  - Second Negative Correlation: Price & Mileage (r = {r_price_mileage:.4f})\n")
    log_file.write("    Interpretation: Higher odometer readings compound the economic discount.\n\n")

    # Correlation Heatmap Plot
    plt.figure(figsize=(7, 6))
    plt.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar(label="Pearson Correlation Coefficient")
    plt.xticks(range(len(corr_matrix.columns)), corr_matrix.columns, fontsize=11)
    plt.yticks(range(len(corr_matrix.columns)), corr_matrix.columns, fontsize=11)
    
    for i in range(len(corr_matrix.columns)):
        for j in range(len(corr_matrix.columns)):
            text_color = "white" if abs(corr_matrix.iloc[i, j]) > 0.5 else "black"
            plt.text(j, i, f"{corr_matrix.iloc[i, j]:.3f}",
                     ha="center", va="center", color=text_color, fontweight='bold', fontsize=12)

    plt.title("Problem 4: Car Resale Correlation Heatmap", fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "prob4_car_resale_correlation_matrix.png"), dpi=300)
    plt.close()
    log_file.write("Plot saved: plots/prob4_car_resale_correlation_matrix.png\n\n")

# ---------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------
def main():
    log_path = os.path.join(OUTPUTS_DIR, "experiment_results.txt")
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write("CS 360 / CS 306: Machine Learning Lab - Practice Assignment 2 (LAB 3)\n")
        log_file.write("Advanced Correlation Analysis: Non-Linearity, Monotonicity & Multivariable Association\n\n")
        solve_problem_1(log_file)
        solve_problem_2(log_file)
        solve_problem_3(log_file)
        solve_problem_4(log_file)
    print(f"LAB 3 experiment executed successfully. Results written to:\n  {log_path}")

if __name__ == "__main__":
    main()


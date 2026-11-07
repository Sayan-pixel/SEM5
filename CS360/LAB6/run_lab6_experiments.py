"""
CS 306 / CS360: Machine Learning Laboratory
Evaluation Assignment 1 (EA1): Multi-Feature Linear Regression with Gradient Descent Variants
Author: 2401179
Department of Computer Science & Engineering, Indian Institute of Information Technology Guwahati

Tasks Covered:
- Q1.(a): Read mental_health_digital_behavior_data.xlsx / hospital.csv, extract features and target ('digital_wellbeing_score').
- Q1.(b): Min-Max Feature Normalization on predictor matrix.
- Q1.(c): Random 3-way dataset splitting:
         1. 60:20:20 (Train:Val:Test)
         2. 70:10:20 (Train:Val:Test)
         3. 80:10:10 (Train:Val:Test)
- Q2.(a): Hyperparameter tuning via Grid Search across all 3 splits:
         - Learning rate alpha in {0.0001, 0.1}
         - Convergence threshold rho (or tau) in {0.001, 0.01}
         - Stopping criterion: |Cost_new - Cost_old| <= rho.
- Q2.(b): Re-train model with optimal hyperparameters and predict hypothesis y_hat.
- Q2.(c): Compute Mean-RSS for all 3 splits on Train and Test sets.
- Q2.(d): Re-implement Q2(a)-(c) using Stochastic Gradient Descent (SGD) without in-built packages.
- Q2.(e): Re-implement Q2(a)-(c) using Mini-Batch Gradient Descent (MBGD) without in-built packages.
- Q2.(f): Plot Mean-RSS (Cost = Mean-RSS / 2) vs Epochs for all three variants of GD on their best splits.
"""

import os
import sys
import tempfile
import numpy as np
import pandas as pd

# Headless matplotlib configuration
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "mpl_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
PLOTS_DIR = os.path.join(SCRIPT_DIR, "plots")
OUTPUTS_DIR = os.path.join(SCRIPT_DIR, "outputs")


def load_data(filepath=None):
    """
    Load dataset from xlsx or csv format.
    Extract predictors X (numerical) and target y ('digital_wellbeing_score').
    """
    if filepath is None:
        xlsx_path = os.path.join(DATA_DIR, "mental_health_digital_behavior_data.xlsx")
        csv_path = os.path.join(DATA_DIR, "hospital.csv")
        if os.path.exists(xlsx_path):
            filepath = xlsx_path
        elif os.path.exists(csv_path):
            filepath = csv_path
        else:
            raise FileNotFoundError("Neither mental_health_digital_behavior_data.xlsx nor hospital.csv found.")

    if filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath)

    df = df.dropna()

    target_col = "digital_wellbeing_score"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset columns: {df.columns.tolist()}")

    X_df = df.drop(columns=[target_col]).select_dtypes(include=[np.number])
    y_df = df[target_col]

    feature_names = X_df.columns.tolist()
    return X_df.values.astype(float), y_df.values.astype(float), feature_names


def min_max_normalize(X):
    """
    Min-Max feature normalization: x_norm = (x - x_min) / (x_max - x_min).
    Prevents division by zero for constant features.
    """
    X_min = np.min(X, axis=0)
    X_max = np.max(X, axis=0)
    range_X = X_max - X_min
    range_X[range_X == 0] = 1.0
    X_norm = (X - X_min) / range_X
    return X_norm, X_min, range_X


def train_val_test_split(X, y, train_ratio, val_ratio, random_state=42):
    """
    Partition dataset into Training, Validation, and Testing sets according to ratios.
    """
    if random_state is not None:
        np.random.seed(random_state)

    n = X.shape[0]
    indices = np.random.permutation(n)

    train_end = int(train_ratio * n)
    val_end = train_end + int(val_ratio * n)

    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]

    return X[train_idx], y[train_idx], X[val_idx], y[val_idx], X[test_idx], y[test_idx]


def compute_cost(X, y, w):
    """
    Mean Squared Cost Function: J(w) = (1 / (2 * N)) * ||Xw - y||^2 = (1 / 2) * Mean-RSS.
    """
    N = len(y)
    predictions = np.dot(X, w)
    cost = (1.0 / (2.0 * N)) * np.sum((predictions - y) ** 2)
    return cost


def compute_mean_rss(X, y, w):
    """
    Mean Residual Sum of Squares (Mean-RSS): (1 / N) * ||Xw - y||^2.
    """
    N = len(y)
    predictions = np.dot(X, w)
    mean_rss = np.sum((predictions - y) ** 2) / N
    return mean_rss


def batch_gradient_descent(X, y, alpha, rho, max_epochs=10000):
    """
    Batch Gradient Descent (BGD) without external ML libraries.
    Stopping criterion: |J(w_new) - J(w_old)| <= rho.
    """
    N, d = X.shape
    w = np.zeros(d)
    cost_history = []

    cost = compute_cost(X, y, w)
    cost_history.append(cost)

    epochs = 0
    while epochs < max_epochs:
        predictions = np.dot(X, w)
        gradients = (1.0 / N) * np.dot(X.T, (predictions - y))
        w = w - alpha * gradients

        new_cost = compute_cost(X, y, w)
        cost_history.append(new_cost)

        if abs(cost - new_cost) <= rho:
            break

        cost = new_cost
        epochs += 1

    return w, cost_history


def stochastic_gradient_descent(X, y, alpha, rho, max_epochs=1000):
    """
    Stochastic Gradient Descent (SGD) updating weights sample-by-sample.
    Stopping criterion: |J(w_new) - J(w_old)| <= rho evaluated per full epoch.
    """
    N, d = X.shape
    w = np.zeros(d)
    cost_history = []

    cost = compute_cost(X, y, w)
    cost_history.append(cost)

    epochs = 0
    while epochs < max_epochs:
        indices = np.random.permutation(N)
        X_shuffled = X[indices]
        y_shuffled = y[indices]

        for i in range(N):
            xi = X_shuffled[i:i + 1]
            yi = y_shuffled[i:i + 1]
            prediction = np.dot(xi, w)
            gradients = np.dot(xi.T, (prediction - yi))
            w = w - alpha * gradients.flatten()

        new_cost = compute_cost(X, y, w)
        cost_history.append(new_cost)

        if abs(cost - new_cost) <= rho:
            break

        cost = new_cost
        epochs += 1

    return w, cost_history


def mini_batch_gradient_descent(X, y, alpha, rho, batch_size=32, max_epochs=2000):
    """
    Mini-Batch Gradient Descent (MBGD) without external ML libraries.
    Stopping criterion: |J(w_new) - J(w_old)| <= rho evaluated per full epoch.
    """
    N, d = X.shape
    w = np.zeros(d)
    cost_history = []

    cost = compute_cost(X, y, w)
    cost_history.append(cost)

    epochs = 0
    while epochs < max_epochs:
        indices = np.random.permutation(N)
        X_shuffled = X[indices]
        y_shuffled = y[indices]

        for i in range(0, N, batch_size):
            X_batch = X_shuffled[i:i + batch_size]
            y_batch = y_shuffled[i:i + batch_size]
            B = len(y_batch)
            predictions = np.dot(X_batch, w)
            gradients = (1.0 / B) * np.dot(X_batch.T, (predictions - y_batch))
            w = w - alpha * gradients

        new_cost = compute_cost(X, y, w)
        cost_history.append(new_cost)

        if abs(cost - new_cost) <= rho:
            break

        cost = new_cost
        epochs += 1

    return w, cost_history


def grid_search(X_train, y_train, X_val, y_val, alphas, rhos, gd_func, **kwargs):
    """
    Grid-search method for hyperparameter tuning across combinations of (alpha, rho).
    Evaluates Mean-RSS on validation set.
    """
    best_w = None
    best_alpha = None
    best_rho = None
    best_val_error = float("inf")
    tuning_log = []

    for alpha in alphas:
        for rho in rhos:
            w, _ = gd_func(X_train, y_train, alpha, rho, **kwargs)
            val_error = compute_mean_rss(X_val, y_val, w)
            tuning_log.append({
                "alpha": alpha,
                "rho": rho,
                "val_mean_rss": val_error
            })
            if val_error < best_val_error:
                best_val_error = val_error
                best_w = w
                best_alpha = alpha
                best_rho = rho

    return best_w, best_alpha, best_rho, best_val_error, tuning_log


def run_experiment(X, y, splits, alphas, rhos, gd_name, gd_func, **kwargs):
    """
    Execute end-to-end experiment for a GD variant across all three dataset splits.
    """
    print(f"\n=======================================================")
    print(f" Running Optimizer: {gd_name}")
    print(f"=======================================================")
    results = {}

    for split_name, (train_r, val_r) in splits.items():
        print(f"\n>>> Split Configuration: {split_name} (Train: {train_r*100:.0f}%, Val: {val_r*100:.0f}%, Test: {(1-train_r-val_r)*100:.0f}%)")
        X_train, y_train, X_val, y_val, X_test, y_test = train_val_test_split(
            X, y, train_r, val_r, random_state=42
        )

        # 2.(a) Grid Search on validation set
        best_w, best_alpha, best_rho, best_val_error, tuning_log = grid_search(
            X_train, y_train, X_val, y_val, alphas, rhos, gd_func, **kwargs
        )
        print(f"  [Tuning Result] Best alpha: {best_alpha}, Best rho: {best_rho} | Val Mean-RSS: {best_val_error:.4f}")

        # 2.(b) Re-train with optimal hyperparameters
        final_w, cost_hist = gd_func(X_train, y_train, best_alpha, best_rho, **kwargs)

        # 2.(c) Mean-RSS computation
        train_rss = compute_mean_rss(X_train, y_train, final_w)
        val_rss = compute_mean_rss(X_val, y_val, final_w)
        test_rss = compute_mean_rss(X_test, y_test, final_w)
        print(f"  [Performance] Train Mean-RSS: {train_rss:.4f} | Val Mean-RSS: {val_rss:.4f} | Test Mean-RSS: {test_rss:.4f}")
        print(f"  [Convergence] Epochs to stop: {len(cost_hist) - 1}")

        results[split_name] = {
            "w": final_w,
            "best_alpha": best_alpha,
            "best_rho": best_rho,
            "train_rss": train_rss,
            "val_rss": val_rss,
            "test_rss": test_rss,
            "cost_history": cost_hist,
            "tuning_log": tuning_log
        }

    best_split = min(results, key=lambda k: results[k]["test_rss"])
    print(f"\n=> Best Performing Split for {gd_name}: {best_split} (Test Mean-RSS = {results[best_split]['test_rss']:.4f})")
    return results, best_split


def main(mini_batch_size=32):
    print("=" * 70)
    print("CS 306 / CS360: Machine Learning Lab - Evaluation Assignment 1")
    print("Multi-Feature Linear Regression: BGD vs SGD vs Mini-Batch GD")
    print("=" * 70)

    # 1.(a) Load data
    X_raw, y, feature_names = load_data()
    print(f"Loaded dataset: {X_raw.shape[0]} samples, {X_raw.shape[1]} features.")
    print(f"Features: {feature_names}")
    print(f"Target: digital_wellbeing_score (Range: [{y.min():.2f}, {y.max():.2f}])")

    # 1.(b) Min-Max feature normalization
    X_norm, X_min, range_X = min_max_normalize(X_raw)
    print("Min-Max normalization completed. Normalized feature matrix shape:", X_norm.shape)

    # Add intercept bias column x_0 = 1
    X = np.hstack([np.ones((X_norm.shape[0], 1)), X_norm])

    # 1.(c) Splits configuration
    splits = {
        "60:20:20": (0.6, 0.2),
        "70:10:20": (0.7, 0.1),
        "80:10:10": (0.8, 0.1)
    }

    # Hyperparameter grids
    alphas = [0.0001, 0.1]
    rhos = [0.001, 0.01]

    # Run experiments for all 3 variants
    # Q2.(a)-(c): Batch GD
    bgd_results, bgd_best = run_experiment(X, y, splits, alphas, rhos, "Batch GD", batch_gradient_descent)

    # Q2.(d): Stochastic GD
    sgd_results, sgd_best = run_experiment(X, y, splits, alphas, rhos, "Stochastic GD", stochastic_gradient_descent)

    # Q2.(e): Mini-Batch GD
    mbgd_results, mbgd_best = run_experiment(
        X, y, splits, alphas, rhos, f"Mini-Batch GD (B={mini_batch_size})",
        mini_batch_gradient_descent, batch_size=mini_batch_size
    )

    # Q2.(f): Plot Mean-RSS (represented by Cost = Mean-RSS / 2) vs Epochs
    plt.figure(figsize=(10, 6))
    plt.plot(bgd_results[bgd_best]["cost_history"], label=f"Batch GD (Split: {bgd_best})", color="#1f77b4", lw=2)
    plt.plot(sgd_results[sgd_best]["cost_history"], label=f"Stochastic GD (Split: {sgd_best})", color="#ff7f0e", lw=2, alpha=0.85)
    plt.plot(mbgd_results[mbgd_best]["cost_history"], label=f"Mini-Batch GD B={mini_batch_size} (Split: {mbgd_best})", color="#2ca02c", lw=2, linestyle="--")

    plt.title("Cost Function J(w) [Mean-RSS / 2] vs. Epochs for Best Performing Splits", fontsize=14, fontweight="bold")
    plt.xlabel("Epochs", fontsize=12)
    plt.ylabel("Cost J(w)", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    best_splits_plot = os.path.join(PLOTS_DIR, "cost_vs_epochs_for_best_splits.png")
    plt.savefig(best_splits_plot, dpi=300)
    plt.close()
    print(f"\n[Artifact Saved] Convergence comparison plot saved to: {best_splits_plot}")

    # Additional individual diagnostic plots for all splits
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
    for idx, (sname, _) in enumerate(splits.items()):
        ax = axes[idx]
        ax.plot(bgd_results[sname]["cost_history"], label="BGD", color="#1f77b4", lw=2)
        ax.plot(sgd_results[sname]["cost_history"], label="SGD", color="#ff7f0e", lw=1.8, alpha=0.85)
        ax.plot(mbgd_results[sname]["cost_history"], label=f"MBGD (B={mini_batch_size})", color="#2ca02c", lw=1.8, linestyle="--")
        ax.set_title(f"Split {sname}", fontsize=12, fontweight="bold")
        ax.set_xlabel("Epochs", fontsize=11)
        if idx == 0:
            ax.set_ylabel("Cost J(w)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(fontsize=10)
    plt.suptitle("Loss Trajectories across All Dataset Splits", fontsize=14, fontweight="bold")
    plt.tight_layout()
    all_splits_plot = os.path.join(PLOTS_DIR, "loss_trajectories_all_splits.png")
    plt.savefig(all_splits_plot, dpi=300)
    plt.close()
    print(f"[Artifact Saved] All splits trajectory plot saved to: {all_splits_plot}")

    # Write comprehensive experiment results to outputs/experiment_results.txt
    results_txt_path = os.path.join(OUTPUTS_DIR, "experiment_results.txt")
    with open(results_txt_path, "w", encoding="utf-8") as f:
        f.write("========================================================================================\n")
        f.write("CS306 / CS360: MACHINE LEARNING LAB - EVALUATION ASSIGNMENT 1 (EA1) REPORT\n")
        f.write("========================================================================================\n\n")
        f.write(f"Dataset Size: {X_raw.shape[0]} samples, {X_raw.shape[1]} predictor features + 1 target.\n")
        f.write(f"Features: {', '.join(feature_names)}\n")
        f.write("Target: digital_wellbeing_score\n\n")

        for name, res, best_s in [
            ("Batch Gradient Descent (BGD)", bgd_results, bgd_best),
            ("Stochastic Gradient Descent (SGD)", sgd_results, sgd_best),
            (f"Mini-Batch Gradient Descent (MBGD, B={mini_batch_size})", mbgd_results, mbgd_best)
        ]:
            f.write(f"----------------------------------------------------------------------------------------\n")
            f.write(f"Optimizer: {name}\n")
            f.write(f"----------------------------------------------------------------------------------------\n")
            f.write(f"Best Overall Split: {best_s} | Test Mean-RSS: {res[best_s]['test_rss']:.6f}\n\n")

            for sname in splits:
                s_res = res[sname]
                f.write(f"  Split [{sname}]:\n")
                f.write(f"    - Optimal Alpha: {s_res['best_alpha']}\n")
                f.write(f"    - Optimal Rho:   {s_res['best_rho']}\n")
                f.write(f"    - Train Mean-RSS: {s_res['train_rss']:.6f}\n")
                f.write(f"    - Val Mean-RSS:   {s_res['val_rss']:.6f}\n")
                f.write(f"    - Test Mean-RSS:  {s_res['test_rss']:.6f}\n")
                f.write(f"    - Epochs Converged: {len(s_res['cost_history']) - 1}\n")
                f.write(f"    - Learned Weights (w0 to wd):\n")
                weight_str = ", ".join([f"w{i}: {w:.4f}" for i, w in enumerate(s_res['w'])])
                f.write(f"      [{weight_str}]\n\n")

        f.write("========================================================================================\n")
        f.write("SUMMARY COMPARISON ACROSS OPTIMIZERS (ON BEST RESPECTIVE SPLITS):\n")
        f.write("========================================================================================\n")
        f.write(f"{'Optimizer':<30} | {'Best Split':<10} | {'Alpha':<8} | {'Rho':<8} | {'Epochs':<8} | {'Test Mean-RSS':<14}\n")
        f.write("-" * 88 + "\n")
        f.write(f"{'Batch GD':<30} | {bgd_best:<10} | {bgd_results[bgd_best]['best_alpha']:<8} | {bgd_results[bgd_best]['best_rho']:<8} | {len(bgd_results[bgd_best]['cost_history'])-1:<8} | {bgd_results[bgd_best]['test_rss']:<14.6f}\n")
        f.write(f"{'Stochastic GD':<30} | {sgd_best:<10} | {sgd_results[sgd_best]['best_alpha']:<8} | {sgd_results[sgd_best]['best_rho']:<8} | {len(sgd_results[sgd_best]['cost_history'])-1:<8} | {sgd_results[sgd_best]['test_rss']:<14.6f}\n")
        f.write(f"{'Mini-Batch GD (B=' + str(mini_batch_size) + ')':<30} | {mbgd_best:<10} | {mbgd_results[mbgd_best]['best_alpha']:<8} | {mbgd_results[mbgd_best]['best_rho']:<8} | {len(mbgd_results[mbgd_best]['cost_history'])-1:<8} | {mbgd_results[mbgd_best]['test_rss']:<14.6f}\n")
        f.write("========================================================================================\n")

    print(f"[Artifact Saved] Comprehensive results report written to: {results_txt_path}")
    print("\nExecution complete.")


if __name__ == "__main__":
    np.random.seed(42)
    # Support command line or prompt mini-batch size
    batch_size = 32
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except ValueError:
            batch_size = 32
    main(mini_batch_size=batch_size)


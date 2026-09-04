from numpy.random import randint
import numpy as np
import pandas  as pd
import matplotlib.pyplot as plt
import os

# CONFIG
# =========

SEED = 42
np.random.seed(SEED)

N = 100
CURRENT_YEAR = 2026

DEFAULT_LEARNING_RATE = 0.01

# No. of GD iterations
ITERATIONS = 10000

#Train-test splits
SPLITS = [
    (20, 80),
    (40, 60),
    (60, 40),
    (80, 20)
]

# Learning rates for Part (g)
LEARNING_RATES = [0.0001, 0.05, 0.1, 1]

# O/P folders
RESULTS_DIR = "results"
PLOT_DIR = "plots"

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# UTILITY FUNCTIONS
# ==================

def standardize_fit(X):
    # Calcuate mean & standard deviation from training data.
    mean = np.mean(X, axis=0)
    std = np.std(X, axis=0)

    std[std == 0] = 1 # Prevent division by zero

    return mean, std

def standardize_transform(X, mean, std):
    # Standardise X using previously calculated mean/std.
    return (X - mean) / std

def add_bias(X):
    # Add a column of 1s for w0/intercept.
    return np.column_stack((np.ones(X.shape[0]), X))

# PART (a) CREATE SYNTHETIC DATASET
# ==================================

def create_dataset():
    np.random.seed(SEED)

    # Mileage
    mileage = np.random.randint(5000, 150001, N)

    # Year of manufacture
    year_of_manufacture = np.random.randint(2010, 2027, N)

    # Age
    age = CURRENT_YEAR - year_of_manufacture

    # Generate resale price
    car_variation = np.random.normal(0, 150000, N)
    base_price = np.random.randint(800000, 3000001, N)
    price = (base_price - 3 * mileage - 50000 * age + car_variation)

    price = np.maximum(price, 200000) # Prevent unrealistic -ve prices

    # Create final Dataset

    df = pd.DataFrame({
        "price": price.round(2),
        "mileage": mileage,
        "age": age
    })

    # Shuffle dataset
    df = df.sample(
        frac=1,
        random_state=SEED
    ).reset_index(drop=True)

    # Add pattern number
    df.insert(0, "pattern", range(1, N + 1))

    # Save datset
    df.to_csv(
        os.path.join(
            RESULTS_DIR,
            "synthetic_car_dataset.csv"
        ),
        index=False
    )

    return df

# PART (b) CREATE TRAINING-TESTING SPLITS
# =======================================

def create_splits(df):
    splits = {}

    total = len(df)

    for train_percent, test_percent in SPLITS:

        train_size = int(
            total * train_percent / 100
        )

        train_df = df.iloc[:train_size].copy()
        test_df = df.iloc[train_size:].copy()

        split_name = (
            f"train_{train_percent}_test_{test_percent}"
        )

        splits[split_name] = (
            train_df,
            test_df
        )

        # Save individual split
        train_df.to_csv(
            os.path.join(
                RESULTS_DIR,
                f"{split_name}_training.csv"
            ),
            index=False
        )

        test_df.to_csv(
            os.path.join(
                RESULTS_DIR,
                f"{split_name}_testing.csv"
            ),
            index=False
        )

    return splits

# GRADIENT DESCENT FROM SCRATCH
def batch_gradient_descent(
    X,
    y,
    learning_rate=0.01,
    iterations=10000,
    initial_weights=None
):
    """
    Batch Gradient Descent for Multiple Linear Regression.

    Hypothesis:

        y_hat = w0 + w1*x1 + w2*x2

    X must already contain the bias column.
    """

    m = len(y)

    # Initialize weights

    if initial_weights is None:
        weights = np.zeros(
            X.shape[1],
            dtype=float
        )
    else:
        weights = np.array(
            initial_weights,
            dtype=float
        )

    cost_history = []

    # Batch Gradient Descent

    for iteration in range(iterations):

        # Prediction
        predictions = X @ weights

        # Error
        error = predictions - y

        # Cost / MSE
        cost = np.mean(error ** 2)

        cost_history.append(cost)

        # Gradient
        gradient = (
            (1 / m)
            * (X.T @ error)
        )

        # Update weights
        weights = (
            weights
            - learning_rate * gradient
        )

        # Stop if numerical overflow occurs
        if not np.all(np.isfinite(weights)):
            break

    return weights, cost_history

# PREDICTION
# ==========
def predict(X, weights):
    return X @ weights

# MSE <Mean Squared Error>
# ===
def calculate_mse(y_actual, y_predicted):
    return np.mean((y_actual - y_predicted) ** 2)

# R^2 -> Coefficient of determination.
# ===================================
def calculate_r2(y_actual, y_predicted):
    ss_res = np.sum (
        (y_actual - y_predicted) ** 2
    )

    ss_tot = np.sum(
        (y_actual - np.mean(y_actual)) ** 2
    )

    if ss_tot == 0:
        return 0

    return 1 - (ss_res / ss_tot)

# CONVERT STANDARDIZED WEIGHTS TO ORIGINAL SCALE
# ==============================================
def convert_weights_to_original_scale(
    standardized_weights, x_mean, x_std,
    y_mean, y_std
):
    w0_standard = standardized_weights[0]
    w1_standard = standardized_weights[1]
    w2_standard = standardized_weights[2]

    w1 = (y_std * w1_standard / x_std[0])
    w2 = (y_std * w2_standard / x_std[1])

    w0 = (
        y_mean
        + y_std * w0_standard
        - w1 * x_mean[0]
        - w2 * x_mean[1]
    )

    return np.array([w0, w1, w2])


def main():
    # 1(a) Create Dataset
    df = create_dataset()
    
    # 1(b) Create Splits
    splits = create_splits(df)
    
    best_split_name = None
    best_mse = float('inf')
    best_split_data = None
    
    report_lines = []
    report_lines.append("=========================================")
    report_lines.append("  MULTIPLE LINEAR REGRESSION REPORT  ")
    report_lines.append("=========================================\n")
    report_lines.append("=== PART 1(c) to 1(f) ===")
    
    split_results = []
    
    # Initialize a 2x2 grid for subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Actual vs Predicted Prices for Different Splits (Question 1)', fontsize=16)
    axes = axes.flatten()
    
    for idx, (split_name, (train_df, test_df)) in enumerate(splits.items()):
        # Prepare data
        X_train = train_df[['mileage', 'age']].values
        y_train = train_df['price'].values
        
        X_test = test_df[['mileage', 'age']].values
        y_test = test_df['price'].values
        
        # Standardize X
        X_mean, X_std = standardize_fit(X_train)
        X_train_std = standardize_transform(X_train, X_mean, X_std)
        X_test_std = standardize_transform(X_test, X_mean, X_std)
        
        # Standardize y (Target Variable)
        y_mean = np.mean(y_train)
        y_std = np.std(y_train)
        if y_std == 0: y_std = 1
        y_train_std = (y_train - y_mean) / y_std
        y_test_std = (y_test - y_mean) / y_std
        
        # Add bias
        X_train_bias = add_bias(X_train_std)
        X_test_bias = add_bias(X_test_std)
        
        # 1(c) Train multiple linear regression models
        weights_std, cost_history = batch_gradient_descent(X_train_bias, y_train_std, learning_rate=DEFAULT_LEARNING_RATE, iterations=ITERATIONS)
        
        # Convert weights to original scale
        weights_orig = convert_weights_to_original_scale(weights_std, X_mean, X_std, y_mean, y_std)
        
        # 1(e) Calculate and store price for testing patterns
        y_pred_std = predict(X_test_bias, weights_std)
        y_pred = y_pred_std * y_std + y_mean
        
        # Store predictions for the test split
        test_df_results = test_df.copy()
        test_df_results['predicted_price'] = y_pred
        test_df_results.to_csv(os.path.join(RESULTS_DIR, f"{split_name}_predictions.csv"), index=False)
        
        # 1(f) Calculate MSE and R^2
        mse = calculate_mse(y_test, y_pred)
        r2 = calculate_r2(y_test, y_pred)
        
        split_results.append({
            'split': split_name,
            'w0': weights_orig[0],
            'w1': weights_orig[1],
            'w2': weights_orig[2],
            'mse': mse,
            'r2': r2
        })
        
        report_lines.append(f"\nSplit: {split_name}")
        report_lines.append(f"  Weights (w0, w1, w2): {weights_orig}")
        report_lines.append(f"  MSE: {mse}")
        report_lines.append(f"  R2 : {r2}")
        
        # 1(d) Visualize plots for different hypotheses on the combined grid
        ax = axes[idx]
        ax.scatter(y_test, y_pred, alpha=0.7, color='b', label='Predicted vs Actual')
        
        # Perfect fit line
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], color='r', linestyle='--', label='Perfect Fit')
        
        ax.set_xlabel("Actual Price")
        ax.set_ylabel("Predicted Price")
        ax.set_title(f"Split: {split_name}")
        ax.legend()
        ax.grid(True)
        
        # Track the best split (lowest MSE)
        if mse < best_mse:
            best_mse = mse
            best_split_name = split_name
            best_split_data = (X_train_bias, y_train_std, X_test_bias, y_test_std, X_mean, X_std, y_mean, y_std, y_test)

    # Save combined plot
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.savefig(os.path.join(PLOT_DIR, "plot_q1_combined.png"))
    plt.close()

    # Save summary of all splits
    pd.DataFrame(split_results).to_csv(os.path.join(RESULTS_DIR, "split_results_summary.csv"), index=False)

    report_lines.append(f"\n=== PART 1(g) ===")
    report_lines.append(f"Best Split selected: {best_split_name} (Lowest MSE: {best_mse})")
    
    # 1(g) Hyperparameter tuning on best split
    X_train_bias, y_train_std, X_test_bias, y_test_std, X_mean, X_std, y_mean, y_std, y_test_orig = best_split_data
    
    hyper_results = []
    
    initializations = {
        "Zeros": np.zeros(3),
        "Random [0,1]": np.random.uniform(0, 1, 3)
    }
    
    for init_name, init_weights in initializations.items():
        report_lines.append(f"\nInitialization Strategy: {init_name}")
        for lr in LEARNING_RATES:
            weights_std, cost_history = batch_gradient_descent(
                X_train_bias, y_train_std, 
                learning_rate=lr, 
                iterations=ITERATIONS, 
                initial_weights=init_weights
            )
            
            # Predict
            y_pred_std = predict(X_test_bias, weights_std)
            y_pred_orig = y_pred_std * y_std + y_mean
            
            mse = calculate_mse(y_test_orig, y_pred_orig)
            r2 = calculate_r2(y_test_orig, y_pred_orig)
            
            # Check if gradient descent diverged
            if not np.all(np.isfinite(weights_std)):
                weights_orig = [np.nan, np.nan, np.nan]
                mse = np.nan
                r2 = np.nan
            else:
                weights_orig = convert_weights_to_original_scale(weights_std, X_mean, X_std, y_mean, y_std)
            
            hyper_results.append({
                'Initialization': init_name,
                'Learning_Rate': lr,
                'w0': weights_orig[0],
                'w1': weights_orig[1],
                'w2': weights_orig[2],
                'MSE': mse,
                'R2': r2
            })
            
            report_lines.append(f"  Learning Rate (alpha): {lr}")
            report_lines.append(f"    Weights (w0, w1, w2): {weights_orig}")
            report_lines.append(f"    MSE: {mse}, R2: {r2}")
            
    # Save hyperparameter tuning results
    pd.DataFrame(hyper_results).to_csv(os.path.join(RESULTS_DIR, "hyperparameter_tuning_results.csv"), index=False)
    
    # 1(h) Generate Report
    report_path = os.path.join(RESULTS_DIR, "report.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
        
    print(f"Question 1 Execution complete. Results and report saved in '{RESULTS_DIR}' and plots in '{PLOT_DIR}'.")

if __name__ == "__main__":
    main()

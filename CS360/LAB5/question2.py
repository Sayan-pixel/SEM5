import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error, r2_score

from question1 import (
    create_dataset, create_splits, standardize_fit, standardize_transform, 
    convert_weights_to_original_scale, RESULTS_DIR, PLOT_DIR, ITERATIONS, LEARNING_RATES
)

def main():
    print("Executing Question 2: In-built library for Gradient Descent (SGDRegressor)")
    
    # Reuse dataset and splits creation
    df = create_dataset()
    splits = create_splits(df)
    
    best_split_name = None
    best_mse = float('inf')
    best_split_data = None
    
    report_lines = []
    report_lines.append("=========================================")
    report_lines.append("  QUESTION 2: SGDRegressor REPORT  ")
    report_lines.append("=========================================\n")
    report_lines.append("=== SKLEARN IMPLEMENTATION RESULTS ===")
    
    split_results = []
    
    # Initialize a 2x2 grid for subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Actual vs Predicted Prices for Different Splits (Question 2 - Sklearn)', fontsize=16)
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
        
        # Train SGDRegressor
        # alpha in sklearn SGDRegressor is regularization term. The learning rate is eta0
        model = SGDRegressor(
            loss='squared_error',
            penalty=None,
            learning_rate='constant',
            eta0=0.01,
            max_iter=ITERATIONS,
            tol=1e-5,
            random_state=42
        )
        
        model.fit(X_train_std, y_train_std)
        
        # Weights
        # The intercept is model.intercept_[0], and coefficients are model.coef_
        weights_std = np.concatenate((model.intercept_, model.coef_))
        
        # Convert weights to original scale
        weights_orig = convert_weights_to_original_scale(weights_std, X_mean, X_std, y_mean, y_std)
        
        # Predict on test set
        y_pred_std = model.predict(X_test_std)
        y_pred = y_pred_std * y_std + y_mean
        
        # Calculate MSE and R^2 using sklearn
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
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
        
        # Visualize plots for different hypotheses (Actual vs Predicted)
        ax = axes[idx]
        ax.scatter(y_test, y_pred, alpha=0.7, color='g', label='Predicted vs Actual (Sklearn)')
        
        # Perfect fit line
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], color='r', linestyle='--', label='Perfect Fit')
        
        ax.set_xlabel("Actual Price")
        ax.set_ylabel("Predicted Price")
        ax.set_title(f"Actual vs Predicted (Sklearn) - {split_name}")
        ax.legend()
        ax.grid(True)
        
        # Track the best split (lowest MSE)
        if mse < best_mse:
            best_mse = mse
            best_split_name = split_name
            best_split_data = (X_train_std, y_train_std, X_test_std, y_test_std, X_mean, X_std, y_mean, y_std, y_test)

    # Save combined plot
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.savefig(os.path.join(PLOT_DIR, "plot_q2_combined.png"))
    plt.close()

    # Save summary of all splits
    pd.DataFrame(split_results).to_csv(os.path.join(RESULTS_DIR, "split_results_summary_q2.csv"), index=False)

    report_lines.append(f"\n=== HYPERPARAMETER TUNING ===")
    report_lines.append(f"Best Split selected: {best_split_name} (Lowest MSE: {best_mse})")
    
    # Hyperparameter tuning on best split
    X_train_std, y_train_std, X_test_std, y_test_std, X_mean, X_std, y_mean, y_std, y_test_orig = best_split_data
    
    hyper_results = []
    
    # We can only adjust learning rate (eta0) easily in SGDRegressor. 
    # For custom initializations, we'd need to use `warm_start` or modify attributes, but typically `fit` resets them.
    # However, SGDRegressor doesn't natively support setting random weights in [0,1] unless we hack it.
    # So we'll iterate over learning rates as requested.
    for lr in LEARNING_RATES:
        model = SGDRegressor(
            loss='squared_error',
            penalty=None,
            learning_rate='constant',
            eta0=lr,
            max_iter=ITERATIONS,
            tol=1e-5,
            random_state=42
        )
        
        try:
            model.fit(X_train_std, y_train_std)
            weights_std = np.concatenate((model.intercept_, model.coef_))
            
            y_pred_std = model.predict(X_test_std)
            y_pred_orig = y_pred_std * y_std + y_mean
            
            mse = mean_squared_error(y_test_orig, y_pred_orig)
            r2 = r2_score(y_test_orig, y_pred_orig)
            
            weights_orig = convert_weights_to_original_scale(weights_std, X_mean, X_std, y_mean, y_std)
            
        except ValueError as e:
            # Catch overflow errors from diverging learning rates
            weights_orig = [np.nan, np.nan, np.nan]
            mse = np.nan
            r2 = np.nan

        hyper_results.append({
            'Learning_Rate': lr,
            'w0': weights_orig[0],
            'w1': weights_orig[1],
            'w2': weights_orig[2],
            'MSE': mse,
            'R2': r2
        })
        
        report_lines.append(f"\n  Learning Rate (alpha): {lr}")
        report_lines.append(f"    Weights (w0, w1, w2): {weights_orig}")
        report_lines.append(f"    MSE: {mse}, R2: {r2}")
            
    # Save hyperparameter tuning results
    pd.DataFrame(hyper_results).to_csv(os.path.join(RESULTS_DIR, "hyperparameter_tuning_results_q2.csv"), index=False)
    
    # Append Report
    report_path = os.path.join(RESULTS_DIR, "report.txt")
    with open(report_path, "a") as f:
        f.write("\n\n" + "\n".join(report_lines))
        
    print(f"Question 2 Execution complete.")

if __name__ == "__main__":
    main()

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1.(a) Read dataset, extract predictors and target.
def load_data(filepath):
    df = pd.read_csv(filepath)
    
    # Drop rows with missing values
    df = df.dropna()
    
    target_col = 'digital_wellbeing_score'
    
    
    X_df = df.drop(columns=[target_col]).select_dtypes(include=[np.number])
    y_df = df[target_col]
    
    return X_df.values, y_df.values

# 1.(b) Normalize the features using Min-Max Normalization
def min_max_normalize(X):

    X_min = np.min(X, axis=0)
    X_max = np.max(X, axis=0)
    
    # Prevent division by zero for constant features
    range_X = X_max - X_min
    range_X[range_X == 0] = 1 
    
    X_norm = (X - X_min) / range_X
    return X_norm

# 1.(c) Randomly splits the dataset into Training, Validation and Testing sets.
def train_val_test_split(X, y, train_ratio, val_ratio):
    n = X.shape[0]
    indices = np.random.permutation(n)
    
    train_end = int(train_ratio * n)
    val_end = train_end + int(val_ratio * n)
    
    train_idx = indices[:train_end]
    val_idx = indices[train_end:val_end]
    test_idx = indices[val_end:]
    
    return X[train_idx], y[train_idx], X[val_idx], y[val_idx], X[test_idx], y[test_idx]

# Mean-RSS (Residual Sum of Squares)
def compute_mean_rss(X, y, w):
    predictions = np.dot(X, w)
    rss = np.sum((predictions - y) ** 2)
    mean_rss = rss / len(y)
    return mean_rss

# Cost function -> J(w) = (1/2N) * RSS.
def compute_cost(X, y, w):
    N = len(y)
    predictions = np.dot(X, w)
    cost = (1 / (2 * N)) * np.sum((predictions - y) ** 2)
    return cost

# Batch Gradient Decent ->
def batch_gradient_descent(X, y, alpha, rho, max_epochs=10000):

    N, d = X.shape
    w = np.zeros(d)
    cost_history = []
    
    cost = compute_cost(X, y, w)
    cost_history.append(cost)
    
    epochs = 0
    while epochs < max_epochs:
        predictions = np.dot(X, w)
        gradients = (1 / N) * np.dot(X.T, (predictions - y))
        w = w - alpha * gradients
        
        new_cost = compute_cost(X, y, w)
        cost_history.append(new_cost)
        
        if abs(cost - new_cost) <= rho:
            break
            
        cost = new_cost
        epochs += 1
        
    return w, cost_history

# Implement Stochastic Gradient Descent   
def stochastic_gradient_descent(X, y, alpha, rho, max_epochs=1000):
    
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
            xi = X_shuffled[i:i+1]
            yi = y_shuffled[i:i+1]
            
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

# Grid-search method for hyper-parameter tuning
def grid_search(X_train, y_train, X_val, y_val, alphas, rhos, gd_func, **kwargs):
    best_w = None
    best_alpha = None
    best_rho = None
    best_val_error = float('inf')
    
    for alpha in alphas:
        for rho in rhos:
            if 'batch_size' in kwargs:
                w, _ = gd_func(X_train, y_train, alpha, rho, kwargs['batch_size'])
            else:
                w, _ = gd_func(X_train, y_train, alpha, rho)
                
            val_error = compute_mean_rss(X_val, y_val, w)
            
            if val_error < best_val_error:
                best_val_error = val_error
                best_w = w
                best_alpha = alpha
                best_rho = rho
                
    return best_w, best_alpha, best_rho, best_val_error

def run_experiment(X, y, splits, alphas, rhos, gd_name, gd_func, **kwargs):
    print(f"\n--- Running {gd_name} ---")
    results = {}
    
    for split_name, (train_r, val_r) in splits.items():
        print(f"\nEvaluating Split: {split_name}")
        X_train, y_train, X_val, y_val, X_test, y_test = train_val_test_split(X, y, train_r, val_r)
        
        # Grid Search
        best_w, best_alpha, best_rho, _ = grid_search(
            X_train, y_train, X_val, y_val, alphas, rhos, gd_func, **kwargs
        )
        print(f"Optimal Hyper-parameters -> alpha: {best_alpha}, rho: {best_rho}")
        
        # Re-train with optimal hyper-parameters
        if 'batch_size' in kwargs:
            final_w, cost_hist = gd_func(X_train, y_train, best_alpha, best_rho, kwargs['batch_size'])
        else:
            final_w, cost_hist = gd_func(X_train, y_train, best_alpha, best_rho)
            
        # Calculate mean-RSS on test set
        train_rss = compute_mean_rss(X_train, y_train, final_w)
        test_rss = compute_mean_rss(X_test, y_test, final_w)
        print(f"Train Mean-RSS: {train_rss:.4f} | Test Mean-RSS: {test_rss:.4f}")
        
        results[split_name] = {
            'w': final_w,
            'test_rss': test_rss,
            'cost_history': cost_hist
        }
        
    # Find best split based on test_rss
    best_split = min(results, key=lambda k: results[k]['test_rss'])
    print(f"Best split for {gd_name} is {best_split}")
    
    return results, best_split


def main():
    X_raw, y = load_data('hospital.csv')
    
    # Normalize features
    X_norm = min_max_normalize(X_raw)
    
    # Add bias term (column of 1s)
    X = np.hstack([np.ones((X_norm.shape[0], 1)), X_norm])
    
    # Configuration
    splits = {
        '60:20:20': (0.6, 0.2),
        '70:10:20': (0.7, 0.1),
        '80:10:10': (0.8, 0.1)
    }
    alphas = [0.0001, 0.1]
    rhos = [0.001, 0.01]
    
    # (a)-(c) Batch GD
    bgd_results, bgd_best = run_experiment(X, y, splits, alphas, rhos, "Batch GD", batch_gradient_descent)
    
    # (d) Stochastic GD
    sgd_results, sgd_best = run_experiment(X, y, splits, alphas, rhos, "Stochastic GD", stochastic_gradient_descent)
    
    # (f) Plot the mean-RSS (represented by the Cost function scaled by 2) during training
    plt.figure(figsize=(12, 6))
    
    plt.plot(bgd_results[bgd_best]['cost_history'], label=f'Batch GD ({bgd_best})')
    plt.plot(sgd_results[sgd_best]['cost_history'], label=f'Stochastic GD ({sgd_best})')
    
    plt.title('Cost (Mean-RSS / 2) vs. Epochs for Best Splits')
    plt.xlabel('Epochs')
    plt.ylabel('Cost')
    plt.legend()
    plt.grid(True)
    plt.show()
if __name__ == "__main__":
    np.random.seed(42)
    main()


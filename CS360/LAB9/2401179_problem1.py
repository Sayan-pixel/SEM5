import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings as wr
import os

np.random.seed(42)
n_samples = 500

# Generating features
amount = np.random.uniform(10, 10000, n_samples)
balance = np.random.uniform(100, 100000, n_samples)
total_transactions = np.random.randint(1, 5000, n_samples)
frequency = np.random.uniform(0.1, 30, n_samples) # per month
time_since_last = np.random.uniform(0, 365, n_samples)

# Creating a target veriable
z = (0.001 * amount - 0.0001 * balance + 0.005 * total_transactions 
     + 0.5 * frequency - 0.02 * time_since_last)

# Apply sigmoid to get probabilities
prob = 1 / (1 + np.exp(-np.clip(z, -250, 250)))
y = (prob > 0.5).astype(int)

# Combine into feature matrix
X_all = np.column_stack((amount, balance, total_transactions, frequency, time_since_last))

# Logistic Regression Function
def sigmoid(z):
    z = np.clip(z, -250, 250) # Clip to prevent numeric overflow
    return 1 / (1 + np.exp(-z))
def compute_cost(X, y, theta):
    m = len(y)
    h = sigmoid(X.dot(theta))
    epsilon = 1e-7 # Prevent log(0)
    cost = -(1/m) * np.sum(y * np.log(h + epsilon) + (1 - y) * np.log(1 - h + epsilon))
    return cost
def sgd_logistic_regression(X, y, alpha=0.01, rho=0.001, max_epochs=500):
    m, n = X.shape
    theta = np.zeros(n)
    cost_history = []
    
    for epoch in range(max_epochs):
        # Stochastic Gradient Descent: update per sample
        indices = np.arange(m)
        np.random.shuffle(indices)
        X_shuffled = X[indices]
        y_shuffled = y[indices]
        
        for i in range(m):
            xi = X_shuffled[i]
            yi = y_shuffled[i]
            hi = sigmoid(np.dot(xi, theta))
            gradient = xi * (hi - yi)
            theta = theta - alpha * gradient
            
        current_cost = compute_cost(X, y, theta)
        cost_history.append(current_cost)
        
        # Stopping criteria: absolute error-difference in two consecutive epochs < rho
        if epoch > 0:
            if abs(cost_history[-2] - cost_history[-1]) < rho:
                break
                
    return theta

# Evaluation and Cross Validation
def get_metrics(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    
    total = len(y_true)
    overall_acc = (tp + tn) / total if total > 0 else 0
    acc_nonfraud = tn / (tn + fp) if (tn + fp) > 0 else 0 # Class-wise accuracy (Class 0)
    acc_fraud = tp / (tp + fn) if (tp + fn) > 0 else 0    # Class-wise accuracy (Class 1)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = acc_fraud
    
    cm = np.array([[tn, fp], [fn, tp]])
    return overall_acc, acc_nonfraud, acc_fraud, precision, recall, cm

def k_fold_cv(X, y, k=5, alpha=0.01, rho=0.001, normalize=False):
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)
    folds = np.array_split(indices, k)
    
    metrics = []
    cms = []
    
    for i in range(k):
        test_idx = folds[i]
        train_idx = np.hstack([folds[j] for j in range(k) if j != i])
        
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        # (c) Feature scaler fitted ONLY on the training set of each fold
        if normalize:
            mean = np.mean(X_train, axis=0)
            std = np.std(X_train, axis=0)
            std[std == 0] = 1 
            X_train = (X_train - mean) / std
            X_test = (X_test - mean) / std
            
        # Add intercept term (column of 1s)
        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        X_test = np.hstack((np.ones((X_test.shape[0], 1)), X_test))
        
        # Train and predict
        theta = sgd_logistic_regression(X_train, y_train, alpha, rho)
        probs = sigmoid(X_test.dot(theta))
        y_pred = (probs >= 0.5).astype(int)
        
        # Collect metrics
        overall_acc, acc_nonfraud, acc_fraud, prec, rec, cm = get_metrics(y_test, y_pred)
        metrics.append([overall_acc, acc_nonfraud, acc_fraud, prec, rec])
        cms.append(cm)
        
    return metrics, cms

# Plot Confusion Matrix
def plot_confusion_matrix(cm, title, filename):
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Non-Fraud (0)', 'Fraud (1)'], 
                yticklabels=['Non-Fraud (0)', 'Fraud (1)'])
    plt.title(title)
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def print_results(metrics, cms, title, filename):
    print(f"\n{'='*60}\n{title}\n{'='*60}")
    cols = ['Overall Acc', 'Acc(Non-Fraud)', 'Acc(Fraud)', 'Precision', 'Recall']
    df_metrics = pd.DataFrame(metrics, columns=cols)
    df_metrics.index = [f'Fold {i+1}' for i in range(len(metrics))]
    print(df_metrics)
    
    print("\n--- Mean Metrics (Across 5 Folds) ---")
    print(df_metrics.mean())
    
    total_cm = np.sum(cms, axis=0)
    print(f"\n--- Combined Confusion Matrix ---")
    print(total_cm)
    
    plot_confusion_matrix(total_cm, title, filename)
    print(f"Saved confusion matrix plot as: {filename}")


if __name__ == "__main__":

    # (b) Binary logistic regression WITHOUT feature scaling
    metrics_b, cms_b = k_fold_cv(X_all, y, normalize=False)
    print_results(metrics_b, cms_b, "1(b): Without Feature Scaling", "CM_1b_Without_Scaling.png")

    # (c & d) Re-implement 1(b) USING Z-score normalization
    metrics_c, cms_c = k_fold_cv(X_all, y, normalize=True)
    print_results(metrics_c, cms_c, "1(c): With Z-score Normalization", "CM_1c_With_Scaling.png")

    # (e & f) Model A: Transaction amount (idx 0) & frequency (idx 3)
    X_model_A = X_all[:, [0, 3]]
    # Normalizing as a standard practice for gradient descent
    metrics_A, cms_A = k_fold_cv(X_model_A, y, normalize=True)
    print_results(metrics_A, cms_A, "1(e) Model A: Amount & Frequency Only", "CM_Model_A.png")

    # (e & f) Model B: All available predictors
    metrics_B, cms_B = k_fold_cv(X_all, y, normalize=True)
    print_results(metrics_B, cms_B, "1(e) Model B: All Predictors", "CM_Model_B.png")

    # (g) Report my observation on which model provides best predictive performance
    print("observations are given in the word document")

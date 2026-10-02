import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set seed for reproducibility
np.random.seed(42)

def sigmoid(z):
    # clip z to avoid overflow
    z = np.clip(z, -250, 250)
    return 1 / (1 + np.exp(-z))

def compute_cost(X, y, theta):
    m = len(y)
    h = sigmoid(X.dot(theta))
    epsilon = 1e-5 # to prevent log(0)
    cost = -(1/m) * np.sum(y * np.log(h + epsilon) + (1 - y) * np.log(1 - h + epsilon))
    return cost

def batch_gradient_descent(X, y, alpha, rho, max_epochs):
    m, n = X.shape
    # Consider model parameters are to be initialized to zero
    theta = np.zeros(n)
    cost_history = []
    
    for epoch in range(max_epochs):
        h = sigmoid(X.dot(theta))
        gradient = (1/m) * X.T.dot(h - y)
        theta = theta - alpha * gradient
        
        current_cost = compute_cost(X, y, theta)
        cost_history.append(current_cost)
        
        # Stopping criteria based on absolute error-difference in two consecutive epochs
        if epoch > 0:
            if abs(cost_history[-2] - cost_history[-1]) < rho:
                break
                
    return theta

def train_one_vs_all(X, y, alpha, rho, max_epochs, num_classes):
    # One-vs-all strategy for multi-class scenario
    thetas = []
    for c in range(num_classes):
        # Create binary targets: 1 if class is c, else 0
        y_binary = (y == c).astype(int)
        theta_c = batch_gradient_descent(X, y_binary, alpha, rho, max_epochs)
        thetas.append(theta_c)
    return np.array(thetas)

def predict_one_vs_all(X, thetas):
    probabilities = sigmoid(X.dot(thetas.T))
    return np.argmax(probabilities, axis=1)

def get_confusion_matrix(y_true, y_pred, num_classes):
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm

def calculate_metrics(cm):
    num_classes = cm.shape[0]
    total = np.sum(cm)
    overall_accuracy = np.trace(cm) / total if total > 0 else 0
    
    class_wise_accuracy = []
    precision = []
    recall = []
    
    for i in range(num_classes):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp
        tn = total - tp - fp - fn
        
        acc = (tp + tn) / total if total > 0 else 0
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        class_wise_accuracy.append(acc)
        precision.append(prec)
        recall.append(rec)
        
    return overall_accuracy, class_wise_accuracy, precision, recall

if __name__ == "__main__":
    print("Loading Iris dataset...")
    df = pd.read_csv('Iris.csv')
    X = df[['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm']].values
    y_labels = df['Species'].values

    # Encode labels
    classes = np.unique(y_labels)
    num_classes = len(classes)
    label_to_idx = {label: idx for idx, label in enumerate(classes)}
    y = np.array([label_to_idx[label] for label in y_labels])

    # Add intercept term to X
    X = np.hstack((np.ones((X.shape[0], 1)), X))

    # Standardize features (except intercept)
    for i in range(1, X.shape[1]):
        X[:, i] = (X[:, i] - np.mean(X[:, i])) / np.std(X[:, i])

    # Hyperparameters to tune
    alphas = [0.0001, 0.1]
    rhos = [0.001, 0.01]
    epochs_list = [50, 100]

    # K-Fold Cross Validation Setup (k=5)
    k = 5
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)
    fold_sizes = np.full(k, len(indices) // k, dtype=int)
    fold_sizes[:len(indices) % k] += 1
    current = 0
    folds = []
    for fold_size in fold_sizes:
        start, stop = current, current + fold_size
        folds.append(indices[start:stop])
        current = stop

    all_fold_metrics = []
    best_fold_idx = -1
    best_fold_accuracy = -1

    for i in range(k):
        print(f"\n--- Fold {i+1} ---")
        test_idx = folds[i]
        train_idx = np.hstack([folds[j] for j in range(k) if j != i])
        
        X_train_full, y_train_full = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        # 10% validation set
        val_size = int(0.10 * len(X_train_full))
        val_idx = np.random.choice(len(X_train_full), val_size, replace=False)
        train_sub_idx = np.setdiff1d(np.arange(len(X_train_full)), val_idx)
        
        X_train, y_train = X_train_full[train_sub_idx], y_train_full[train_sub_idx]
        X_val, y_val = X_train_full[val_idx], y_train_full[val_idx]
        
        best_val_acc = -1
        best_params = None
        best_thetas = None
        
        for alpha in alphas:
            for rho in rhos:
                for max_epochs in epochs_list:
                    thetas = train_one_vs_all(X_train, y_train, alpha, rho, max_epochs, num_classes)
                    y_val_pred = predict_one_vs_all(X_val, thetas)
                    val_acc = np.mean(y_val_pred == y_val)
                    if val_acc > best_val_acc:
                        best_val_acc = val_acc
                        best_params = (alpha, rho, max_epochs)
                        best_thetas = thetas
                        
        print(f"Best params: alpha={best_params[0]}, rho={best_params[1]}, epochs={best_params[2]} (Val Acc: {best_val_acc:.4f})")
        
        # Evaluate on test set
        y_test_pred = predict_one_vs_all(X_test, best_thetas)
        cm = get_confusion_matrix(y_test, y_test_pred, num_classes)
        
        # Visualize confusion matrix
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
        plt.title(f'Confusion Matrix - Fold {i+1}')
        plt.ylabel('Actual Targets')
        plt.xlabel('Predicted Hypothesis')
        plt.tight_layout()
        plt.savefig(f'confusion_matrix_fold_{i+1}.png')
        plt.close()
        
        overall_accuracy, class_wise_accuracy, precision, recall = calculate_metrics(cm)
        
        fold_result = {
            'Fold': i + 1,
            'Overall Accuracy': overall_accuracy,
            'Accuracy (Setosa)': class_wise_accuracy[0],
            'Accuracy (Versicolor)': class_wise_accuracy[1],
            'Accuracy (Virginica)': class_wise_accuracy[2],
            'Precision (Setosa)': precision[0],
            'Precision (Versicolor)': precision[1],
            'Precision (Virginica)': precision[2],
            'Recall (Setosa)': recall[0],
            'Recall (Versicolor)': recall[1],
            'Recall (Virginica)': recall[2]
        }
        all_fold_metrics.append(fold_result)
        print(f"Test Accuracy: {overall_accuracy:.4f}")
        
        if overall_accuracy > best_fold_accuracy:
            best_fold_accuracy = overall_accuracy
            best_fold_idx = i

    print(f"\nBest fold was Fold {best_fold_idx + 1} with accuracy {best_fold_accuracy:.4f}")

    # Calculate averages
    avg_metrics = {}
    for key in all_fold_metrics[0].keys():
        if key != 'Fold':
            avg_metrics[key] = np.mean([f[key] for f in all_fold_metrics])
    avg_metrics['Fold'] = 'Average'

    # Prepare dataframes for export
    df_all_folds = pd.DataFrame(all_fold_metrics)
    df_avg = pd.DataFrame([avg_metrics])
    df_best = pd.DataFrame([all_fold_metrics[best_fold_idx]])

    # Export to separate sheets
    with pd.ExcelWriter('Problem1_Results.xlsx') as writer:
        df_all_folds.to_excel(writer, sheet_name='All Folds Metrics', index=False)
        df_avg.to_excel(writer, sheet_name='Average Metrics', index=False)
        df_best.to_excel(writer, sheet_name='Best Fold Metrics', index=False)

    print("\n[+] Results written to 'Problem1_Results.xlsx'")
    print("[+] Confusion matrices saved as PNG images (confusion_matrix_fold_1.png to 5).")
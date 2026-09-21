import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Custom implementations to replace sklearn utilities

def custom_train_test_split(X, y, test_size=0.2, random_state=None):
    if random_state is not None:
        np.random.seed(random_state)
    indices = np.random.permutation(len(X))
    test_samples = int(len(X) * test_size)
    test_idx = indices[:test_samples]
    train_idx = indices[test_samples:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]

class CustomStandardScaler:
    def fit_transform(self, X):
        self.mean_ = np.mean(X, axis=0)
        self.std_ = np.std(X, axis=0)
        self.std_[self.std_ == 0] = 1 # Avoid division by zero
        return (X - self.mean_) / self.std_
        
    def transform(self, X):
        return (X - self.mean_) / self.std_

def custom_confusion_matrix(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    return np.array([[tn, fp], [fn, tp]])

def custom_accuracy_score(y_true, y_pred):
    return np.mean(y_true == y_pred)

def custom_precision_score(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    return tp / (tp + fp) if (tp + fp) > 0 else 0.0

def custom_recall_score(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    return tp / (tp + fn) if (tp + fn) > 0 else 0.0

def custom_kfold_split(X, n_splits=5, random_state=None):
    if random_state is not None:
        np.random.seed(random_state)
    indices = np.random.permutation(len(X))
    fold_sizes = np.full(n_splits, len(X) // n_splits, dtype=int)
    fold_sizes[:len(X) % n_splits] += 1
    current = 0
    splits = []
    for fold_size in fold_sizes:
        start, stop = current, current + fold_size
        test_idx = indices[start:stop]
        train_idx = np.concatenate((indices[:start], indices[stop:]))
        splits.append((train_idx, test_idx))
        current = stop
    return splits

class CustomLogisticRegression:
    def __init__(self, alpha=0.01, rho=0.001, epochs=100, threshold=0.5):
        self.alpha = alpha
        self.rho = rho
        self.epochs = epochs
        self.threshold = threshold
        self.w = None
        
    def sigmoid(self, z):
        z = np.clip(z, -250, 250)
        return 1 / (1 + np.exp(-z))
        
    def compute_loss(self, y, y_pred):
        m = len(y)
        eps = 1e-15
        y_pred = np.clip(y_pred, eps, 1 - eps)
        loss = - (1/m) * np.sum(y * np.log(y_pred) + (1-y) * np.log(1-y_pred))
        return loss

    def fit(self, X, y):
        m, n = X.shape
        self.w = np.zeros(n)
        loss_history = []
        
        for epoch in range(self.epochs):
            z = np.dot(X, self.w)
            y_pred = self.sigmoid(z)
            
            loss = self.compute_loss(y, y_pred)
            
            if len(loss_history) > 0:
                loss_diff = abs(loss_history[-1] - loss)
                if loss_diff < self.rho:
                    loss_history.append(loss)
                    break
                    
            loss_history.append(loss)
            
            gradient = np.dot(X.T, (y_pred - y)) / m
            self.w -= self.alpha * gradient
            
    def predict_proba(self, X):
        return self.sigmoid(np.dot(X, self.w))
        
    def predict(self, X, threshold=None):
        if threshold is None:
            threshold = self.threshold
        return (self.predict_proba(X) >= threshold).astype(int)

def evaluate_and_plot(y_true, y_pred, title):
    cm = custom_confusion_matrix(y_true, y_pred)
    acc = custom_accuracy_score(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    class_0_acc = tn / (tn + fp) if (tn + fp) > 0 else 0
    class_1_acc = tp / (tp + fn) if (tp + fn) > 0 else 0
    prec = custom_precision_score(y_true, y_pred)
    rec = custom_recall_score(y_true, y_pred)
    
    return {
        'accuracy': acc,
        'class_0_acc': class_0_acc,
        'class_1_acc': class_1_acc,
        'precision': prec,
        'recall': rec,
        'cm': cm
    }

def main():
    # 1. Load Data
    dataset_path = r'e:\IIIT G\SEM_5\CS360\LAB7\diabetes_prediction_dataset.csv'
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    # Preprocessing
    df = pd.get_dummies(df, columns=['gender', 'smoking_history'], drop_first=True)
    X = df.drop('diabetes', axis=1).astype(float).values
    y = df['diabetes'].values
    
    # Scale features and add bias
    scaler = CustomStandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = np.c_[np.ones(X_scaled.shape[0]), X_scaled]
    
    print("\n====== PART A & B: Data Splitting & Hyper-parameter Tuning ======")
    # (a) Random split 80:20
    X_train_full, X_test, y_train_full, y_test = custom_train_test_split(X_scaled, y, test_size=0.2, random_state=42)
    # 10% of training set as validation set
    X_train, X_val, y_train, y_val = custom_train_test_split(X_train_full, y_train_full, test_size=0.1, random_state=42)
    
    # (b) Hyper-parameter tuning
    alphas = [0.0001, 0.1]
    rhos = [0.001, 0.01]
    epochs_list = [50, 100]
    
    best_val_acc = -1
    best_params = {}
    
    for alpha in alphas:
        for rho in rhos:
            for epochs in epochs_list:
                model = CustomLogisticRegression(alpha=alpha, rho=rho, epochs=epochs)
                model.fit(X_train, y_train)
                y_val_pred = model.predict(X_val)
                val_acc = custom_accuracy_score(y_val, y_val_pred)
                
                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    best_params = {'alpha': alpha, 'rho': rho, 'epochs': epochs}
                    
    print(f"Best Hyper-parameters found: {best_params} with Validation Accuracy: {best_val_acc:.4f}")
    
    # Train best custom model on full training data
    best_model = CustomLogisticRegression(**best_params)
    best_model.fit(X_train_full, y_train_full)
    
    # Train built-in model for comparison
    from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
    builtin_model = SklearnLogisticRegression(max_iter=100)
    # Exclude bias column for sklearn as it adds its own by default (fit_intercept=True)
    builtin_model.fit(X_train_full[:, 1:], y_train_full)
    builtin_acc = custom_accuracy_score(y_test, builtin_model.predict(X_test[:, 1:]))
    print(f"Sklearn Built-in Logistic Regression Test Accuracy: {builtin_acc:.4f}")
    
    print("\n====== PART C: Evaluation with Threshold = 0.5 ======")
    y_test_pred_05 = best_model.predict(X_test, threshold=0.5)
    metrics_05 = evaluate_and_plot(y_test, y_test_pred_05, "Confusion Matrix (Threshold 0.5)")
    print("Metrics for Threshold = 0.5:")
    for k, v in metrics_05.items():
        if k != 'cm': print(f"  {k}: {v:.4f}")
        
    print("\n====== PART D: Evaluation with Varying Thresholds ======")
    y_test_pred_03 = best_model.predict(X_test, threshold=0.3)
    metrics_03 = evaluate_and_plot(y_test, y_test_pred_03, "Confusion Matrix (Threshold 0.3)")
    print("Generated Confusion Matrix for Threshold = 0.3")
    
    y_test_pred_07 = best_model.predict(X_test, threshold=0.7)
    metrics_07 = evaluate_and_plot(y_test, y_test_pred_07, "Confusion Matrix (Threshold 0.7)")
    print("Generated Confusion Matrix for Threshold = 0.7")
    
    # Combine plots into one frame
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    sns.heatmap(metrics_03['cm'], annot=True, fmt='d', cmap='Blues', ax=axes[0])
    axes[0].set_title('Threshold 0.3')
    axes[0].set_xlabel('Predicted')
    axes[0].set_ylabel('Actual')
    
    sns.heatmap(metrics_05['cm'], annot=True, fmt='d', cmap='Blues', ax=axes[1])
    axes[1].set_title('Threshold 0.5')
    axes[1].set_xlabel('Predicted')
    axes[1].set_ylabel('Actual')
    
    sns.heatmap(metrics_07['cm'], annot=True, fmt='d', cmap='Blues', ax=axes[2])
    axes[2].set_title('Threshold 0.7')
    axes[2].set_xlabel('Predicted')
    axes[2].set_ylabel('Actual')
    
    plt.tight_layout()
    plt.savefig('Combined_Confusion_Matrices.png')
    plt.show(block=False)
    plt.pause(5)
    plt.close()
    
    print("\n====== PART E: Comparison & Observations ======")
    print("Threshold 0.3 -> Precision: {:.4f}, Recall: {:.4f}, FP: {}, FN: {}".format(
        metrics_03['precision'], metrics_03['recall'], metrics_03['cm'][0,1], metrics_03['cm'][1,0]))
    print("Threshold 0.5 -> Precision: {:.4f}, Recall: {:.4f}, FP: {}, FN: {}".format(
        metrics_05['precision'], metrics_05['recall'], metrics_05['cm'][0,1], metrics_05['cm'][1,0]))
    print("Threshold 0.7 -> Precision: {:.4f}, Recall: {:.4f}, FP: {}, FN: {}".format(
        metrics_07['precision'], metrics_07['recall'], metrics_07['cm'][0,1], metrics_07['cm'][1,0]))
    
    print("\nObservations (Part E):")
    print("As the classification threshold increases from 0.3 to 0.7:")
    print("- The model requires a higher predicted probability to classify a patient as Diabetic.")
    print("- False Positives (FP) decrease, leading to an increase in Precision.")
    print("- False Negatives (FN) increase, leading to a decrease in Recall.")
    
    print("\n====== PART F & G: K-Fold Cross Validation (K=5) ======")
    splits = custom_kfold_split(X_scaled, n_splits=5, random_state=42)
    fold = 1
    
    fold_metrics = []
    
    for train_index, test_index in splits:
        X_train_k_full, X_test_k = X_scaled[train_index], X_scaled[test_index]
        y_train_k_full, y_test_k = y[train_index], y[test_index]
        
        # 10% validation
        X_train_k, X_val_k, y_train_k, y_val_k = custom_train_test_split(X_train_k_full, y_train_k_full, test_size=0.1, random_state=42)
        
        best_val_acc_k = -1
        best_params_k = {}
        for alpha in alphas:
            for rho in rhos:
                for epochs in epochs_list:
                    model = CustomLogisticRegression(alpha=alpha, rho=rho, epochs=epochs)
                    model.fit(X_train_k, y_train_k)
                    val_acc = custom_accuracy_score(y_val_k, model.predict(X_val_k))
                    if val_acc > best_val_acc_k:
                        best_val_acc_k = val_acc
                        best_params_k = {'alpha': alpha, 'rho': rho, 'epochs': epochs}
        
        best_model_k = CustomLogisticRegression(**best_params_k)
        best_model_k.fit(X_train_k_full, y_train_k_full)
        y_pred_k = best_model_k.predict(X_test_k)
        
        metrics_k = evaluate_and_plot(y_test_k, y_pred_k, title="")
        fold_metrics.append(metrics_k)
        print(f"\n--- Fold {fold} ---")
        print(f"Confusion Matrix:\n{metrics_k['cm']}")
        print(f"Accuracy: {metrics_k['accuracy']:.4f}")
        print(f"Class 0 Acc: {metrics_k['class_0_acc']:.4f}, Class 1 Acc: {metrics_k['class_1_acc']:.4f}")
        print(f"Precision: {metrics_k['precision']:.4f}, Recall: {metrics_k['recall']:.4f}")
        fold += 1
        
    avg_accuracy = np.mean([m['accuracy'] for m in fold_metrics])
    avg_class_0_acc = np.mean([m['class_0_acc'] for m in fold_metrics])
    avg_class_1_acc = np.mean([m['class_1_acc'] for m in fold_metrics])
    avg_precision = np.mean([m['precision'] for m in fold_metrics])
    avg_recall = np.mean([m['recall'] for m in fold_metrics])
    
    best_fold_idx = np.argmax([m['accuracy'] for m in fold_metrics])
    best_fold_metrics = fold_metrics[best_fold_idx]
    
    print("\n--- Average across 5 folds ---")
    print(f"Overall Accuracy: {avg_accuracy:.4f}")
    print(f"Class 0 Accuracy: {avg_class_0_acc:.4f}")
    print(f"Class 1 Accuracy: {avg_class_1_acc:.4f}")
    print(f"Precision: {avg_precision:.4f}")
    print(f"Recall: {avg_recall:.4f}")
    
    print(f"\n--- Best Fold (Fold {best_fold_idx + 1}) ---")
    print(f"Overall Accuracy: {best_fold_metrics['accuracy']:.4f}")
    print(f"Class 0 Accuracy: {best_fold_metrics['class_0_acc']:.4f}")
    print(f"Class 1 Accuracy: {best_fold_metrics['class_1_acc']:.4f}")
    print(f"Precision: {best_fold_metrics['precision']:.4f}")
    print(f"Recall: {best_fold_metrics['recall']:.4f}")
    
    print("\n====== PART H: Observations on Splitting vs K-Fold ======")
    print("Random 80:20 Split Accuracy: {:.4f}".format(metrics_05['accuracy']))
    print("K-Fold Average Accuracy: {:.4f}".format(avg_accuracy))
    print("Observations: ")
    print("1. Both Random Splitting and K-Fold provide very similar overall accuracy, suggesting the dataset is large enough and distributions are stable.")
    print("2. K-Fold cross-validation provides a more reliable and robust estimate of model performance because it averages results over multiple distinct test sets.")
    print("3. Random Splitting runs faster, but might be susceptible to lucky/unlucky splits. K-fold mitigates variance in model evaluation metrics.")

if __name__ == '__main__':
    main()

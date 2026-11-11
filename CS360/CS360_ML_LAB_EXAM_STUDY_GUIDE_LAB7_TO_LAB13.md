# CS360 Machine Learning Lab — Complete Pen-and-Paper Exam Study Guide (LAB7 to LAB13)

> **Purpose of this Guide:** Prepared strictly from `LAB7` through `LAB13` in `CS360` for **pen-and-paper lab exams** (no IDE, no laptop). Every ML program is broken down into its **standard execution stages**, showing **exact exam-writable code**, **what each library/function/line does**, **mathematical formulas**, and **observations/viva points**.

---

## Table of Contents

1. [Part 0: Universal ML Program Structure & Common Stages (Memorize First!)](#part-0-universal-ml-program-structure--common-stages)
2. [LAB 7 (PA5): Binary Logistic Regression (Batch GD), Decision Thresholds & 5-Fold CV](#lab-7-pa5-binary-logistic-regression-batch-gd-decision-thresholds--5-fold-cv)
3. [LAB 8 (PA6): Multi-Class Logistic Regression (One-vs-All) & K-Means Clustering + PCA](#lab-8-pa6-multi-class-logistic-regression-one-vs-all--k-means-clustering--pca)
4. [LAB 9 (EA2): Binary Logistic Regression via SGD, Feature Scaling & Feature Subsets](#lab-9-ea2-binary-logistic-regression-via-sgd-feature-scaling--feature-subsets)
5. [LAB 10 (PA7): DBSCAN (Grid Search + K-Distance Elbow) & Hierarchical Clustering from Scratch](#lab-10-pa7-dbscan-grid-search--k-distance-elbow--hierarchical-clustering-from-scratch)
6. [LAB 11 (EA3): DBSCAN with Scikit-Learn, Standardization & Silhouette Score](#lab-11-ea3-dbscan-with-scikit-learn-standardization--silhouette-score)
7. [LAB 12 (PA8): Standard vs Weighted K-NN & Continuous-Attribute ID3 Decision Tree](#lab-12-pa8-standard-vs-weighted-k-nn--continuous-attribute-id3-decision-tree)
8. [LAB 13 (PA9): Perceptron (OR/NAND), Categorical Naive Bayes & Gaussian Naive Bayes](#lab-13-pa9-perceptron-ornand-categorical-naive-bayes--gaussian-naive-bayes)
9. [Final Quick-Revision Formula & Exam Cheat Sheet](#final-quick-revision-formula--exam-cheat-sheet)

---

## Part 0: Universal ML Program Structure & Common Stages

Almost every ML lab program in CS360 follows **8 standard stages**. If you memorize this skeleton, you can write any ML program on paper by plugging in the specific algorithm in Stage 5!

### Stage 0.1: Importing Libraries

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Used when built-in / sklearn implementations are allowed or for comparison:
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import dendrogram
```

| Library | Alias / Module | Purpose in CS360 Labs |
| :--- | :--- | :--- |
| **NumPy** | `np` | Matrix/vector math, dot products (`np.dot`), math functions (`np.exp`, `np.log`, `np.sqrt`), random shuffling/sampling, arrays. |
| **Pandas** | `pd` | Reading CSV files (`pd.read_csv`), one-hot encoding (`pd.get_dummies`), dropping/selecting columns, exporting tables/Excel. |
| **Matplotlib** | `plt` | Plotting scatter plots, line plots (K-distance graph), subplots (`plt.subplots`), saving figures (`plt.savefig`). |
| **Seaborn** | `sns` | Plotting Confusion Matrices cleanly via `sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')`. |
| **Scikit-learn** | `sklearn` | Built-in ML models (`LogisticRegression`, `DBSCAN`), preprocessing (`StandardScaler`), metrics (`silhouette_score`). |
| **SciPy** | `scipy.cluster.hierarchy` | Plotting dendrograms (`dendrogram(Z)`) from linkage matrix `Z`. |
| **Built-in Python** | `math`, `random` | Used in LAB13 when even NumPy/Pandas are avoided (`math.exp`, `math.log`, `math.sqrt`, `random.uniform`, `random.shuffle`). |

---

### Stage 0.2: Common Preprocessing Functions (Reusable Across Labs)

#### A. Z-Score Standardization (Feature Scaling)
Formula: $X_{\text{scaled}} = \frac{X - \mu}{\sigma}$

```python
# From Scratch (NumPy):
mean = np.mean(X_train, axis=0)
std = np.std(X_train, axis=0)
std[std == 0] = 1.0          # Prevent division by zero
X_train_scaled = (X_train - mean) / std
X_test_scaled = (X_test - mean) / std   # Always use TRAIN mean & std on test!

# Using Scikit-Learn:
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```
* **Why needed?** Prevents features with large numeric ranges (e.g., `balance = 100,000`, `PM10 = 150`) from dominating gradient updates (Logistic Regression/SGD) or Euclidean distances (K-Means, DBSCAN, K-NN).
* **Exam rule:** Always compute `mean` and `std` (or call `.fit()`) **ONLY on training data**, then transform test data to avoid **data leakage**.

#### B. Adding Bias / Intercept Column ($x_0 = 1$)
```python
X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
# OR: X = np.c_[np.ones(X.shape[0]), X]
```
* **Why needed?** Allows writing $z = w_0 \cdot 1 + w_1 x_1 + \dots + w_n x_n = X \cdot \theta$ cleanly as one dot product.
* **Note:** Drop column `0` (`X[:, 1:]`) when passing to `sklearn.linear_model.LogisticRegression`, because `sklearn` adds its own intercept (`fit_intercept=True`).

---

### Stage 0.3: Common Data Splitting Functions (Reusable Across Labs)

#### A. Random 80:20 Train-Test Split (From Scratch)
```python
def custom_train_test_split(X, y, test_size=0.2, random_state=42):
    np.random.seed(random_state)
    indices = np.random.permutation(len(X))
    test_samples = int(len(X) * test_size)
    test_idx = indices[:test_samples]
    train_idx = indices[test_samples:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]
```

#### B. K-Fold Cross-Validation Split ($K = 5$)
```python
np.random.seed(42)
indices = np.arange(len(X))
np.random.shuffle(indices)
folds = np.array_split(indices, 5)   # Splits indices into 5 nearly equal arrays

for i in range(5):
    test_idx = folds[i]
    train_idx = np.hstack([folds[j] for j in range(5) if j != i])
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
```
* **How `np.array_split` works:** Automatically handles lengths not divisible by $K$ (unlike simple slicing). `np.hstack` combines the remaining $K-1$ folds into `train_idx`.

---

### Stage 0.4: Common Classification Evaluation Metrics (Reusable Across Labs)

#### Binary Confusion Matrix & Metrics
Layout: $\begin{bmatrix} TN & FP \\ FN & TP \end{bmatrix}$ (Rows = Actual $0, 1$; Columns = Predicted $0, 1$)

```python
def evaluate_binary(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    cm = np.array([[tn, fp], [fn, tp]])

    accuracy = (tp + tn) / len(y_true)
    class_0_acc = tn / (tn + fp) if (tn + fp) > 0 else 0.0   # Specificity
    class_1_acc = tp / (tp + fn) if (tp + fn) > 0 else 0.0   # Recall / Sensitivity
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    return cm, accuracy, class_0_acc, class_1_acc, precision, recall
```

#### Multi-Class Confusion Matrix & Metrics (Used in LAB8, LAB12, LAB13)
```python
def get_confusion_matrix(y_true, y_pred, num_classes):
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm

def calculate_metrics(cm):
    num_classes = cm.shape[0]
    total = np.sum(cm)
    overall_acc = np.trace(cm) / total if total > 0 else 0.0
    class_acc, precision, recall = [], [], []
    for i in range(num_classes):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp
        tn = total - tp - fp - fn
        class_acc.append((tp + tn) / total)
        precision.append(tp / (tp + fp) if (tp + fp) > 0 else 0.0)
        recall.append(tp / (tp + fn) if (tp + fn) > 0 else 0.0)
    return overall_acc, class_acc, precision, recall
```
* **Important Function:** `np.trace(cm)` sums the diagonal elements (all $TP_i$, i.e., total correct predictions).

---

## LAB 7 (PA5): Binary Logistic Regression (Batch GD), Decision Thresholds & 5-Fold CV

**Files Read:** `LAB7/2401179_PA5.py`, `LAB7/run_lab7_experiments.py`, `LAB7/PA5_CS32.pdf`  
**Problem Statement:** Classify diabetic vs non-diabetic patients (`diabetes_prediction_dataset.csv`) using **Logistic Regression from scratch (Batch Gradient Descent)**, compare with `sklearn`, evaluate decision thresholds `{0.3, 0.5, 0.7}`, and perform **5-Fold Cross-Validation** with hyperparameter tuning.

### Stage 1: Importing Libraries
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression as SklearnLogisticRegression
```
* **Use Case:** NumPy for matrix gradient descent, Pandas for CSV + one-hot encoding, Matplotlib & Seaborn for plotting 3 confusion matrices side-by-side, `sklearn` only for benchmarking in Part (b).

### Stage 2: Loading & Preprocessing Data (One-Hot Encoding + Scaling + Bias)
```python
df = pd.read_csv("diabetes_prediction_dataset.csv")

# One-hot encode categorical string columns ('gender', 'smoking_history')
df = pd.get_dummies(df, columns=['gender', 'smoking_history'], drop_first=True)

X = df.drop('diabetes', axis=1).astype(float).values
y = df['diabetes'].values.astype(int)

# Z-score standardization
mean = np.mean(X, axis=0)
std = np.std(X, axis=0)
std[std == 0] = 1.0
X_scaled = (X - mean) / std

# Prepend bias column x0 = 1
X_design = np.c_[np.ones(X_scaled.shape[0]), X_scaled]
```
* **`pd.get_dummies(..., drop_first=True)`:** Converts categorical text columns into binary $0/1$ columns and drops one category per feature to avoid multicollinearity (dummy variable trap).
* **`.astype(float).values`:** Converts boolean/mixed dummy columns into a pure NumPy float array.

### Stage 3: Train / Validation / Test Splitting
```python
# 80% train_full, 20% test
X_train_full, X_test, y_train_full, y_test = custom_train_test_split(
    X_design, y, test_size=0.2, random_state=42
)
# 10% of training set reserved as validation set for tuning
X_train, X_val, y_train, y_val = custom_train_test_split(
    X_train_full, y_train_full, test_size=0.1, random_state=42
)
```
* **Why 3 splits?** `X_train` updates weights, `X_val` picks the best `(alpha, rho, epochs)`, and `X_test` remains completely unseen for final evaluation.

### Stage 4: Logistic Regression Model (Batch Gradient Descent from Scratch)
```python
class CustomLogisticRegression:
    def __init__(self, alpha=0.01, rho=0.001, epochs=100, threshold=0.5):
        self.alpha = alpha
        self.rho = rho
        self.epochs = epochs
        self.threshold = threshold
        self.w = None

    def sigmoid(self, z):
        z = np.clip(z, -250, 250)          # Prevents exp() overflow
        return 1.0 / (1.0 + np.exp(-z))

    def compute_loss(self, y, y_pred):
        m = len(y)
        eps = 1e-15
        y_pred = np.clip(y_pred, eps, 1.0 - eps)  # Prevents log(0)
        return -(1.0 / m) * np.sum(y * np.log(y_pred) + (1.0 - y) * np.log(1.0 - y_pred))

    def fit(self, X, y):
        m, n = X.shape
        self.w = np.zeros(n)               # Initialize parameters to zero
        loss_history = []

        for epoch in range(self.epochs):
            z = np.dot(X, self.w)
            y_pred = self.sigmoid(z)
            loss = self.compute_loss(y, y_pred)

            # Stopping criterion: |loss_prev - loss_curr| <= rho
            if len(loss_history) > 0 and abs(loss_history[-1] - loss) <= self.rho:
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
```
* **Math Behind Batch GD:**
  * Hypothesis: $\hat{y} = \sigma(X w) = \frac{1}{1 + e^{-Xw}}$
  * Binary Cross-Entropy Loss: $J(w) = -\frac{1}{m} \sum_{i=1}^m \left[ y_i \log(\hat{y}_i) + (1 - y_i)\log(1 - \hat{y}_i) \right]$
  * Gradient (averaged over all $m$ samples): $\nabla J(w) = \frac{1}{m} X^T (\hat{y} - y)$
  * Update rule: $w \leftarrow w - \alpha \nabla J(w)$

### Stage 5: Hyperparameter Tuning (Grid Search) & Sklearn Comparison
```python
alphas = [0.0001, 0.1]
rhos = [0.001, 0.01]
epochs_list = [50, 100]

best_val_acc = -1.0
best_params = {}

for alpha in alphas:
    for rho in rhos:
        for epochs in epochs_list:
            model = CustomLogisticRegression(alpha=alpha, rho=rho, epochs=epochs)
            model.fit(X_train, y_train)
            val_acc = np.mean(model.predict(X_val) == y_val)
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_params = {'alpha': alpha, 'rho': rho, 'epochs': epochs}

# Retrain best custom model on full training data
best_model = CustomLogisticRegression(**best_params)
best_model.fit(X_train_full, y_train_full)

# Built-in sklearn comparison (skip bias column 0 using [:, 1:])
builtin_model = SklearnLogisticRegression(max_iter=100)
builtin_model.fit(X_train_full[:, 1:], y_train_full)
builtin_acc = np.mean(builtin_model.predict(X_test[:, 1:]) == y_test)
```

### Stage 6: Threshold Sensitivity Evaluation (0.3 vs 0.5 vs 0.7) & Plotting
```python
y_pred_03 = best_model.predict(X_test, threshold=0.3)
y_pred_05 = best_model.predict(X_test, threshold=0.5)
y_pred_07 = best_model.predict(X_test, threshold=0.7)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for idx, (thresh, y_p) in enumerate([(0.3, y_pred_03), (0.5, y_pred_05), (0.7, y_pred_07)]):
    cm, acc, c0, c1, prec, rec = evaluate_binary(y_test, y_p)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx], cbar=False)
    axes[idx].set_title(f"Threshold = {thresh}")
    axes[idx].set_xlabel("Predicted")
    axes[idx].set_ylabel("Actual")
plt.tight_layout()
plt.savefig("Combined_Confusion_Matrices.png")
```

### Stage 7: 5-Fold Cross-Validation Loop
```python
splits = custom_kfold_split(X_design, n_splits=5, random_state=42)
fold_metrics = []

for train_idx, test_idx in splits:
    X_tr_full, X_te = X_design[train_idx], X_design[test_idx]
    y_tr_full, y_te = y[train_idx], y[test_idx]

    # 10% validation inside each fold for tuning
    X_tr, X_val, y_tr, y_val = custom_train_test_split(X_tr_full, y_tr_full, test_size=0.1, random_state=42)
    # (Run same 3-nested loop grid search to get best_params_k)
    model_k = CustomLogisticRegression(**best_params_k)
    model_k.fit(X_tr_full, y_tr_full)
    y_pred_k = model_k.predict(X_te, threshold=0.5)
    # Store metrics, then compute np.mean(...) across folds and np.argmax(accuracies) for best fold
```

### Stage 8: Key Exam Observations (LAB7)
1. **Effect of Threshold (0.3 $\to$ 0.5 $\to$ 0.7):**
   * Lower threshold (`0.3`): Predicts positive easily $\implies$ **FP increases, FN decreases** $\implies$ **High Recall, Low Precision** (good for medical screening so fewer sick patients are missed).
   * Higher threshold (`0.7`): Strict positive boundary $\implies$ **FP decreases, FN increases** $\implies$ **High Precision, Low Recall**.
2. **80:20 Split vs 5-Fold CV:** On large datasets ($N=100{,}000$), accuracies are nearly identical; however, **5-Fold CV** tests every sample once and gives a lower-variance, more reliable generalization estimate.

---

## LAB 8 (PA6): Multi-Class Logistic Regression (One-vs-All) & K-Means Clustering + PCA

**Files Read:** `LAB8/Problem1.py`, `LAB8/Problem2.py`, `LAB8/run_lab8_experiments.py`, `LAB8/PA6_CS32.pdf`

### Problem 1: Multi-Class Logistic Regression (One-vs-All) on `Iris.csv`

#### Stage 1: Imports & Loading / Encoding Iris Dataset
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(42)
df = pd.read_csv('Iris.csv')
X_raw = df[['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm']].values
y_labels = df['Species'].values

# Encode string labels ('Iris-setosa', etc.) -> integers 0, 1, 2
classes = np.unique(y_labels)
num_classes = len(classes)
label_to_idx = {label: idx for idx, label in enumerate(classes)}
y = np.array([label_to_idx[label] for label in y_labels])

# Standardize features & prepend bias column x0 = 1
X_scaled = (X_raw - np.mean(X_raw, axis=0)) / np.std(X_raw, axis=0)
X = np.hstack((np.ones((X_scaled.shape[0], 1)), X_scaled))
```

#### Stage 2: One-vs-All (OvA) Binary Classifiers via Batch GD
```python
def sigmoid(z):
    z = np.clip(z, -250, 250)
    return 1.0 / (1.0 + np.exp(-z))

def compute_cost(X, y, theta):
    m = len(y)
    h = sigmoid(X.dot(theta))
    eps = 1e-15
    return -(1.0 / m) * np.sum(y * np.log(h + eps) + (1.0 - y) * np.log(1.0 - h + eps))

def batch_gradient_descent(X, y, alpha, rho, max_epochs):
    m, n = X.shape
    theta = np.zeros(n)
    cost_history = []
    for epoch in range(max_epochs):
        h = sigmoid(X.dot(theta))
        gradient = (1.0 / m) * X.T.dot(h - y)
        theta = theta - alpha * gradient
        current_cost = compute_cost(X, y, theta)
        cost_history.append(current_cost)
        if epoch > 0 and abs(cost_history[-2] - cost_history[-1]) <= rho:
            break
    return theta

def train_one_vs_all(X, y, alpha, rho, max_epochs, num_classes):
    thetas = []
    for c in range(num_classes):
        y_binary = (y == c).astype(int)     # 1 for class c, 0 for all other classes
        theta_c = batch_gradient_descent(X, y_binary, alpha, rho, max_epochs)
        thetas.append(theta_c)
    return np.array(thetas)                 # Shape: (num_classes, n_features)

def predict_one_vs_all(X, thetas):
    probabilities = sigmoid(X.dot(thetas.T)) # Shape: (m_samples, num_classes)
    return np.argmax(probabilities, axis=1)  # Pick class with highest probability
```
* **How One-vs-All works:** For $K=3$ classes, trains $3$ separate binary logistic regression classifiers. At test time, passes sample $x$ through all $3$ models and chooses $\arg\max_c P(y=c \mid x)$.

#### Stage 3: 5-Fold CV, Tuning & Exporting to Multi-Sheet Excel
```python
# Inside each fold of 5-fold CV:
# 1. Split X_train_full into 90% X_train and 10% X_val
# 2. Grid search alpha in [0.0001, 0.1], rho in [0.001, 0.01], epochs in [50, 100]
# 3. Evaluate best_thetas on X_test -> cm (3x3), overall_acc, class_acc, precision, recall
# 4. Plot heatmap & track best_fold_idx

# Export to 3 separate sheets in Excel:
with pd.ExcelWriter('Problem1_Results.xlsx') as writer:
    df_all_folds.to_excel(writer, sheet_name='All Folds Metrics', index=False)
    df_avg.to_excel(writer, sheet_name='Average Metrics', index=False)
    df_best.to_excel(writer, sheet_name='Best Fold Metrics', index=False)
```

---

### Problem 2: Unsupervised K-Means Clustering + Custom PCA on `WineQT.csv`

#### Stage 1: Load Unlabeled Data & Standardize
```python
df = pd.read_csv('WineQT.csv')
# Drop target 'quality' and 'Id' because clustering is UNSUPERVISED
drop_cols = [c for c in ['Id', 'quality'] if c in df.columns]
X = df.drop(columns=drop_cols).values.astype(float)

# Standardize features (crucial for distance-based K-Means)
X_scaled = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
```

#### Stage 2: K-Means Algorithm from Scratch
```python
def k_means(X, K, max_iters=1000):
    n_samples, n_features = X.shape
    # Randomly select K data points as initial centroids (without replacement)
    random_indices = np.random.choice(n_samples, K, replace=False)
    centroids = X[random_indices].copy()
    cluster_assignments = np.zeros(n_samples, dtype=int)

    for epoch in range(max_iters):
        # 1. Assignment Step: Euclidean distance from every point to every centroid
        # X[:, np.newaxis, :] is (N, 1, D); centroids[np.newaxis, :, :] is (1, K, D)
        distances = np.linalg.norm(X[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
        new_assignments = np.argmin(distances, axis=1)

        # 2. Stopping Criterion: No change in cluster assignments
        if np.array_equal(cluster_assignments, new_assignments):
            break

        cluster_assignments = new_assignments

        # 3. Update Step: Recompute each centroid as the mean of assigned points
        for k in range(K):
            cluster_points = X[cluster_assignments == k]
            if len(cluster_points) > 0:
                centroids[k] = np.mean(cluster_points, axis=0)

    return cluster_assignments, centroids
```
* **Alternative exam-friendly distance loop** (if you forget broadcasting):
  ```python
  distances = np.zeros((n_samples, K))
  for k in range(K):
      distances[:, k] = np.linalg.norm(X - centroids[k], axis=1)
  ```
* **Inertia (WCSS) formula:** $\text{WCSS} = \sum_{k=1}^K \sum_{x \in C_k} \|x - \mu_k\|^2$.

#### Stage 3: Custom PCA to Reduce High-D Data to 2D for Visualization
```python
def get_first_two_pcs(X):
    covariance_matrix = np.cov(X.T)                 # Covariance matrix (D x D)
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    sorted_indices = np.argsort(eigenvalues)[::-1]  # Descending order
    top_two_eigenvectors = eigenvectors[:, sorted_indices[:2]]
    X_pca = np.dot(X, top_two_eigenvectors)         # Project N x D -> N x 2
    return np.real(X_pca)                           # Discard tiny imaginary float noise
```
* **Why PCA?** `WineQT` has 11 chemical features; PCA projects clusters onto the top 2 principal components so they can be plotted on a 2D scatter grid (`plt.subplot(2, 2, i+1)` for `K in [3, 5, 10, 15]`).

#### Stage 4: Key Exam Observations (LAB8 Problem 2)
* As $K$ increases ($3 \to 5 \to 10 \to 15$), WCSS decreases monotonically, clusters become smaller and heavily overlapping in 2D PCA space (over-segmentation).

---

## LAB 9 (EA2): Binary Logistic Regression via SGD, Feature Scaling & Feature Subsets

**Files Read:** `LAB9/2401179_problem1.py`, `LAB9/run_lab9_experiments.py`, `LAB9/EA2_CS32.pdf`  
**Problem Statement:** Generate a 500-sample synthetic fraud dataset with 5 differently-scaled features, implement **Stochastic Gradient Descent (SGD)** Binary Logistic Regression with 5-Fold CV, compare **Without Scaling (1b)** vs **With Z-Score Normalization (1c)**, and compare **Model A (2 features)** vs **Model B (all 5 features)**.

### Stage 1: Synthetic Dataset Generation (Disparate Feature Scales)
```python
np.random.seed(42)
n_samples = 500

amount = np.random.uniform(10, 10000, n_samples)
balance = np.random.uniform(100, 100000, n_samples)
total_transactions = np.random.randint(1, 5000, n_samples)
frequency = np.random.uniform(0.1, 30, n_samples)
time_since_last = np.random.uniform(0, 365, n_samples)

z = (0.001 * amount - 0.0001 * balance + 0.005 * total_transactions
     + 0.5 * frequency - 0.02 * time_since_last)
prob = 1 / (1 + np.exp(-np.clip(z, -250, 250)))
y = (prob > 0.5).astype(int)

X_all = np.column_stack((amount, balance, total_transactions, frequency, time_since_last))
```

### Stage 2: Stochastic Gradient Descent (SGD) Logistic Regression
```python
def sgd_logistic_regression(X, y, alpha=0.01, rho=0.001, max_epochs=500):
    m, n = X.shape
    theta = np.zeros(n)
    cost_history = []

    for epoch in range(max_epochs):
        # Shuffle samples at the start of every epoch
        indices = np.arange(m)
        np.random.shuffle(indices)
        X_shuffled = X[indices]
        y_shuffled = y[indices]

        # Update weights ONCE PER SAMPLE (unlike Batch GD!)
        for i in range(m):
            xi = X_shuffled[i]
            yi = y_shuffled[i]
            hi = sigmoid(np.dot(xi, theta))
            gradient = xi * (hi - yi)
            theta = theta - alpha * gradient

        current_cost = compute_cost(X, y, theta)
        cost_history.append(current_cost)

        # Stopping criterion: |cost_prev - cost_curr| < rho
        if epoch > 0 and abs(cost_history[-2] - cost_history[-1]) < rho:
            break

    return theta
```
* **Batch GD (LAB7/8) vs SGD (LAB9) — Key Exam Difference:**
  * **Batch GD:** Updates $\theta$ **once per epoch** using average gradient over all $m$ samples: $\frac{1}{m} X^T (h - y)$.
  * **SGD:** Shuffles data each epoch and updates $\theta$ **$m$ times per epoch** (once per sample $i$): $\theta \leftarrow \theta - \alpha (h_i - y_i) x_i$.

### Stage 3: 5-Fold CV with Leak-Free Z-Score Normalization
```python
def k_fold_cv(X, y, k=5, alpha=0.01, rho=0.001, normalize=False):
    indices = np.arange(X.shape[0])
    np.random.shuffle(indices)
    folds = np.array_split(indices, k)

    metrics, cms = [], []
    for i in range(k):
        test_idx = folds[i]
        train_idx = np.hstack([folds[j] for j in range(k) if j != i])
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]

        # Fit scaler ONLY on training fold, then apply to test fold
        if normalize:
            mean = np.mean(X_train, axis=0)
            std = np.std(X_train, axis=0)
            std[std == 0] = 1.0
            X_train = (X_train - mean) / std
            X_test = (X_test - mean) / std

        # Add intercept column of 1s
        X_train = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
        X_test = np.hstack((np.ones((X_test.shape[0], 1)), X_test))

        theta = sgd_logistic_regression(X_train, y_train, alpha, rho)
        y_pred = (sigmoid(X_test.dot(theta)) >= 0.5).astype(int)
        # Compute metrics & append to metrics, cms
    return metrics, cms
```

### Stage 4: Running the 4 Experiments (1b, 1c, Model A, Model B)
```python
# 1(b): Without Feature Scaling
metrics_b, cms_b = k_fold_cv(X_all, y, normalize=False)

# 1(c): With Z-score Normalization
metrics_c, cms_c = k_fold_cv(X_all, y, normalize=True)

# 1(e) Model A: Transaction amount (col 0) & frequency (col 3) only
X_model_A = X_all[:, [0, 3]]
metrics_A, cms_A = k_fold_cv(X_model_A, y, normalize=True)

# 1(e) Model B: All 5 predictors
metrics_B, cms_B = k_fold_cv(X_all, y, normalize=True)
```

### Stage 5: Key Exam Observations (LAB9)
1. **Unscaled vs Z-Score Scaling:** Without scaling, `account_balance` ($\le 100{,}000$) and `amount` ($\le 10{,}000$) cause huge gradients that saturate `sigmoid` immediately, making the model predict only the majority class (Non-Fraud accuracy drops near 0%). Scaling creates spherical loss contours so SGD converges smoothly.
2. **Model A vs Model B:** Model B (all 5 features) achieves higher accuracy and actually detects non-fraud cases, whereas Model A misses vital predictors (`balance`, `total_transactions`, `time_since_last`).

---

## LAB 10 (PA7): DBSCAN (Grid Search + K-Distance Elbow) & Hierarchical Clustering from Scratch

**Files Read:** `LAB10/answer.py`, `LAB10/PA7_CS32.pdf`  
**Problem Statement:** Cluster `Mall_Customers.csv` using:
1. **DBSCAN from scratch** (Grid Search over `minpts` $\in \{4..10\}$, `eps` $\in \{2, 2.5, 3, 3.5, 4\}$, plus **K-Distance Graph** to find optimal `eps` for best `minpts`).
2. **Hierarchical Clustering from scratch** (`single`, `complete`, and `centroid` linkage) + Dendrogram plotting.

### Stage 1: Imports & Data Preparation
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram  # Only used for visual dendrogram

df = pd.read_csv("Mall_Customers.csv")
X = df.iloc[:, [3, 4]].values  # 'Annual Income (k$)' and 'Spending Score (1-100)'
```

### Stage 2: DBSCAN from Scratch (Region Query + BFS Cluster Expansion)
```python
def euclidean_distance(p1, p2):
    return np.sqrt(np.sum((p1 - p2) ** 2))

def region_query(X, point_idx, eps):
    return [i for i in range(len(X)) if euclidean_distance(X[point_idx], X[i]) <= eps]

def dbscan_scratch(X, eps, minpts):
    labels = np.full(len(X), 0)   # 0 = unvisited, -1 = noise, >0 = cluster ID
    cluster_id = 0

    for i in range(len(X)):
        if labels[i] != 0:        # Skip already processed points
            continue

        neighbors = region_query(X, i, eps)
        if len(neighbors) < minpts:
            labels[i] = -1        # Temporarily mark as noise (could become border point later)
        else:
            cluster_id += 1
            labels[i] = cluster_id
            queue = [n for n in neighbors if n != i]
            while queue:
                q_point = queue.pop(0)
                if labels[q_point] == -1:
                    labels[q_point] = cluster_id   # Noise -> Border point
                if labels[q_point] == 0:
                    labels[q_point] = cluster_id
                    q_neighbors = region_query(X, q_point, eps)
                    if len(q_neighbors) >= minpts: # q_point is also a Core point
                        queue.extend(q_neighbors)
    return labels
```
* **Core vs Border vs Noise Point:**
  * **Core point:** Has $\ge \text{minPts}$ points within radius $\varepsilon$.
  * **Border point:** Has $< \text{minPts}$ neighbors, but lies within $\varepsilon$ of a core point.
  * **Noise point (`-1`):** Neither core nor border.

### Stage 3: Silhouette Score from Scratch & Grid Search
```python
def silhouette_score_scratch(X, labels):
    unique_labels = np.unique(labels)
    if len(unique_labels) <= 1 or (len(unique_labels) == 2 and -1 in unique_labels):
        return -1

    s_scores = []
    for i in range(len(X)):
        if labels[i] == -1:
            continue
        same_cluster = X[labels == labels[i]]
        a_i = np.mean([euclidean_distance(X[i], p) for p in same_cluster if not np.array_equal(X[i], p)]) if len(same_cluster) > 1 else 0

        b_i = float('inf')
        for cl in unique_labels:
            if cl == labels[i] or cl == -1:
                continue
            other_cluster = X[labels == cl]
            b_i = min(b_i, np.mean([euclidean_distance(X[i], p) for p in other_cluster]))

        s_i = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0
        s_scores.append(s_i)
    return np.mean(s_scores) if s_scores else -1

# Grid search over eps in [2, 2.5, 3, 3.5, 4] and minpts in range(4, 11)
```
* **Formula:** $s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$, where $a(i)$ = mean intra-cluster distance, $b(i)$ = mean distance to nearest neighboring cluster. Range is $[-1, +1]$; closer to $+1$ is better.

### Stage 4: K-Distance Graph & Elbow Detection for Optimal $\varepsilon$
```python
def k_distance_graph(X, k):
    distances = []
    for i in range(len(X)):
        dists = sorted([euclidean_distance(X[i], X[j]) for j in range(len(X)) if i != j])
        distances.append(dists[k - 1])     # Distance to k-th nearest neighbor

    distances.sort(reverse=True)           # Sort descending

    # Line connecting first point p1 and last point p2 to find maximum perpendicular distance (elbow)
    p1 = np.array([0, distances[0]])
    p2 = np.array([len(distances) - 1, distances[-1]])
    u = p2 - p1
    u_norm = np.linalg.norm(u)

    max_dist, optimal_eps = 0, distances[0]
    for i, d in enumerate(distances):
        v = np.array([i, d]) - p1
        cross_2d = u[0] * v[1] - u[1] * v[0]
        dist_to_line = abs(cross_2d) / u_norm
        if dist_to_line > max_dist:
            max_dist = dist_to_line
            optimal_eps = d

    plt.plot(distances)
    plt.axhline(y=optimal_eps, color='r', linestyle='--')
    plt.show()
    return optimal_eps
```

### Stage 5: Agglomerative Hierarchical Clustering from Scratch
```python
def hierarchical_clustering_scratch(X, linkage='single'):
    n = len(X)
    Z = np.zeros((n - 1, 4))             # Linkage matrix: [c1, c2, dist, merged_size]
    clusters = {i: [i] for i in range(n)}
    centroids = {i: X[i] for i in range(n)}

    dist_matrix = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(i + 1, n):
            dist_matrix[i, j] = dist_matrix[j, i] = euclidean_distance(X[i], X[j])

    next_id = n
    active = list(range(n))

    for step in range(n - 1):
        # Find closest active pair (c1, c2)
        min_dist, c1, c2 = np.inf, -1, -1
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                idx1, idx2 = active[i], active[j]
                if dist_matrix[idx1, idx2] < min_dist:
                    min_dist, c1, c2 = dist_matrix[idx1, idx2], idx1, idx2

        # Merge c1 and c2
        clusters[next_id] = clusters[c1] + clusters[c2]
        s1, s2 = len(clusters[c1]), len(clusters[c2])
        centroids[next_id] = (s1 * centroids[c1] + s2 * centroids[c2]) / (s1 + s2)
        Z[step] = [c1, c2, min_dist, s1 + s2]

        active.remove(c1)
        active.remove(c2)

        # Expand dist_matrix by 1 row & 1 column for new merged cluster
        new_mat = np.full((dist_matrix.shape[0] + 1, dist_matrix.shape[1] + 1), np.inf)
        new_mat[:-1, :-1] = dist_matrix
        dist_matrix = new_mat

        for ac in active:
            if linkage == 'single':
                d = min(dist_matrix[c1, ac], dist_matrix[c2, ac])
            elif linkage == 'complete':
                d = max(dist_matrix[c1, ac], dist_matrix[c2, ac])
            elif linkage == 'centroid':
                d = euclidean_distance(centroids[next_id], centroids[ac])
            dist_matrix[next_id, ac] = dist_matrix[ac, next_id] = d

        active.append(next_id)
        next_id += 1
    return Z

# Plot dendrogram:
# dendrogram(Z, truncate_mode='lastp', p=30)
```
* **Linkage Types:**
  * **Single:** $d(A, B) = \min_{x \in A, y \in B} d(x, y)$ (can cause chaining).
  * **Complete:** $d(A, B) = \max_{x \in A, y \in B} d(x, y)$ (produces compact spherical clusters).
  * **Centroid:** $d(A, B) = d(\mu_A, \mu_B)$ (can cause inversions in dendrograms).

---

## LAB 11 (EA3): DBSCAN with Scikit-Learn, Standardization & Silhouette Score

**Files Read:** `LAB11/2401179_Q1.py`, `LAB11/run_lab10_experiments.py`, `LAB11/EA3_CS32.pdf`  
**Problem Statement:** Cluster urban air quality monitoring stations (`PM2.5`, `PM10`, `NO2`, `SO2`) using `sklearn.cluster.DBSCAN` across 5 `(eps, minPts)` settings, standardize features, plot `PM2.5` vs `PM10`, and compute Silhouette Score only when valid ($2 \le K \le N - 1$, excluding noise).

### Stage 1: Imports
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
```

### Stage 2: Load, Clean & Standardize Data
```python
FEATURES = ["PM2.5", "PM10", "NO2", "SO2"]
df = pd.read_csv("synthetic_urban_air_quality.csv")
df.columns = [str(col).strip() for col in df.columns]

data = df[FEATURES].copy()
for feature in FEATURES:
    data[feature] = pd.to_numeric(data[feature], errors="coerce")
data = data.dropna().reset_index(drop=True)

# Z-score standardization
scaler = StandardScaler()
X_scaled = scaler.fit_transform(data)
```
* **Why Standardization is Mandatory:** `PM10` ranges $>150\ \mu g/m^3$ while `SO2` is $<25\ \mu g/m^3$. Without `StandardScaler`, Euclidean distances in DBSCAN are dominated completely by `PM10`.

### Stage 3: Run DBSCAN Across 5 Parameter Settings & Compute Silhouette Score
```python
PARAMETERS = [
    {"eps": 0.5, "min_samples": 3},
    {"eps": 1.2, "min_samples": 3},
    {"eps": 2.1, "min_samples": 3},
    {"eps": 0.8, "min_samples": 5},
    {"eps": 0.8, "min_samples": 7},
]

for i, params in enumerate(PARAMETERS, start=1):
    model = DBSCAN(eps=params["eps"], min_samples=params["min_samples"])
    labels = model.fit_predict(X_scaled)

    cluster_labels = sorted(set(labels) - {-1})
    n_clusters = len(cluster_labels)
    n_noise = int(np.sum(labels == -1))
    noise_pct = (n_noise / len(labels)) * 100.0

    # Filter out noise points (-1) before Silhouette Score
    valid_mask = labels != -1
    valid_labels = labels[valid_mask]

    silhouette = np.nan
    if valid_mask.sum() >= 3:
        unique_clusters, cluster_counts = np.unique(valid_labels, return_counts=True)
        # Condition: 2 <= K <= N_valid - 1 and clusters have > 1 observation
        if (len(unique_clusters) >= 2
                and len(unique_clusters) < valid_mask.sum()
                and np.all(cluster_counts > 1)):
            silhouette = silhouette_score(X_scaled[valid_mask], valid_labels)
```

### Stage 4: Scatter Plot (`PM2.5` vs `PM10`) & Pollutant Summary
```python
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
axes = axes.flatten()
for i, (labels, params) in enumerate(zip(all_labels, PARAMETERS)):
    ax = axes[i]
    for label in sorted(set(labels)):
        mask = labels == label
        if label == -1:
            ax.scatter(data.loc[mask, "PM2.5"], data.loc[mask, "PM10"],
                       c="black", marker="x", s=60, label="Noise")
        else:
            ax.scatter(data.loc[mask, "PM2.5"], data.loc[mask, "PM10"],
                       s=55, alpha=0.8, label=f"Cluster {label}")
    ax.set_title(f"eps={params['eps']}, minPts={params['min_samples']}")
    ax.legend()
axes[-1].axis("off")   # Hide unused 6th subplot

# Cluster-wise pollutant summary table:
cluster_data = data.copy()
cluster_data["Cluster"] = labels
summary = cluster_data[cluster_data["Cluster"] != -1].groupby("Cluster")[FEATURES].agg(["count", "mean", "min", "max"])
```

### Stage 5: Key Exam Observations (LAB11)
1. **Effect of `eps`:** Very small `eps` (0.5) marks many points as noise (34%); large `eps` (1.2, 2.1) merges everything into 1 single cluster (0% noise).
2. **Effect of `minPts`:** Holding `eps=0.8`, increasing `minPts` from 5 to 7 increases the core density requirement $\implies$ noise percentage increases (12% $\to$ 22%).
3. **Why can't Silhouette Score be computed around noise points?** Noise (`-1`) is NOT a real cluster—points labeled `-1` can be scattered at opposite ends of the feature space. Including `-1` as a cluster artificially destroys intra-cluster distance $a(i)$ and invalidates the score. Also, when `K=1` (e.g., `eps=1.2` or `2.1`), Silhouette Score is undefined because $K < 2$.

---

## LAB 12 (PA8): Standard vs Weighted K-NN & Continuous-Attribute ID3 Decision Tree

**Files Read:** `LAB12/run_lab11_experiments.py`, `LAB12/PA8_CS32.pdf`

### Problem 1: Standard K-NN vs Weighted K-NN (`heart.csv`)

#### Stage 1: Load & Z-Score Standardize
```python
df = pd.read_csv("heart.csv")
feature_cols = [c for c in df.columns if c != "target"]
X_raw = df[feature_cols].values.astype(float)
y = df["target"].values.astype(int)

mean = np.mean(X_raw, axis=0)
std = np.std(X_raw, axis=0)
std[std == 0] = 1.0
X_scaled = (X_raw - mean) / std
```
* **Why scale for K-NN?** K-NN relies on Euclidean distance; unscaled attributes like cholesterol (`~250`) would outweigh binary/small attributes (`~0-1`).

#### Stage 2: Standard K-NN & Weighted K-NN Classifier Class
```python
class KNNClassifier:
    def __init__(self, k=3, weighted=False, epsilon=0.01):
        self.k = k
        self.weighted = weighted
        self.epsilon = epsilon

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y

    def predict(self, X_test):
        predictions = []
        for x in X_test:
            dists = np.linalg.norm(self.X_train - x, axis=1)
            neighbor_idx = np.argsort(dists)[:self.k]
            neighbor_labels = self.y_train[neighbor_idx]
            neighbor_dists = dists[neighbor_idx]

            if not self.weighted:
                # Standard K-NN: simple majority vote
                unique, counts = np.unique(neighbor_labels, return_counts=True)
                pred = unique[np.argmax(counts)]
            else:
                # Weighted K-NN: inverse-distance weights w_i = 1 / (d_i + epsilon)
                weights = 1.0 / (neighbor_dists + self.epsilon)
                weighted_scores = {c: 0.0 for c in np.unique(self.y_train)}
                for lbl, w in zip(neighbor_labels, weights):
                    weighted_scores[lbl] += w
                pred = max(weighted_scores, key=weighted_scores.get)
            predictions.append(pred)
        return np.array(predictions)
```
* **Key Formula:** $w_i = \frac{1}{d_i + \epsilon}$ ($\epsilon = 0.01$ avoids division by zero when $d_i = 0$).
* **Observation:** Weighted K-NN outperforms Standard K-NN across $K \in \{3, 5, 7\}$ because closer neighbors have stronger influence than distant boundary neighbors.

---

### Problem 2: Continuous-Attribute ID3 Decision Tree (`diabetes_prediction_dataset.csv`)

#### Stage 1: Entropy & Information Gain Functions
```python
def entropy(y):
    if len(y) == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    probs = counts / len(y)
    return -np.sum(probs * np.log2(probs + 1e-15))

def information_gain(X_column, y, threshold):
    parent_entropy = entropy(y)
    left_mask = X_column <= threshold
    right_mask = ~left_mask
    if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
        return 0.0
    n = len(y)
    n_l, n_r = np.sum(left_mask), np.sum(right_mask)
    child_entropy = (n_l / n) * entropy(y[left_mask]) + (n_r / n) * entropy(y[right_mask])
    return parent_entropy - child_entropy
```
* **Formulas:**
  * Entropy: $H(S) = -\sum_{c} p_c \log_2(p_c)$
  * Information Gain: $IG(S, A \le t) = H(S) - \left( \frac{|S_L|}{|S|} H(S_L) + \frac{|S_R|}{|S|} H(S_R) \right)$

#### Stage 2: Node Class & Recursive ID3 Tree with Thresholding
```python
class DecisionTreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature = feature
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value

    @property
    def is_leaf(self):
        return self.value is not None

class ID3DecisionTree:
    def __init__(self, max_depth=6, min_samples_split=15):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None

    def fit(self, X, y):
        self.root = self._grow_tree(X, y, depth=0)

    def _grow_tree(self, X, y, depth=0):
        n_samples, n_features = X.shape
        n_labels = len(np.unique(y))

        # Stopping Conditions: Pure node, max depth, or too few samples
        if n_labels == 1 or depth >= self.max_depth or n_samples < self.min_samples_split:
            unique, counts = np.unique(y, return_counts=True)
            return DecisionTreeNode(value=unique[np.argmax(counts)])

        best_gain, best_feat, best_thresh = -1.0, None, None
        for feat_idx in range(n_features):
            col_vals = X[:, feat_idx]
            # Candidate thresholds for continuous attributes (percentiles 10% to 90%)
            thresholds = np.percentile(col_vals, np.linspace(10, 90, 9))
            for thresh in thresholds:
                gain = information_gain(col_vals, y, thresh)
                if gain > best_gain:
                    best_gain, best_feat, best_thresh = gain, feat_idx, thresh

        if best_gain <= 1e-5:   # No useful split / attribute exhaustion
            unique, counts = np.unique(y, return_counts=True)
            return DecisionTreeNode(value=unique[np.argmax(counts)])

        left_mask = X[:, best_feat] <= best_thresh
        left_child = self._grow_tree(X[left_mask], y[left_mask], depth + 1)
        right_child = self._grow_tree(X[~left_mask], y[~left_mask], depth + 1)
        return DecisionTreeNode(feature=best_feat, threshold=best_thresh, left=left_child, right=right_child)

    def _traverse_tree(self, x, node):
        if node.is_leaf:
            return node.value
        if x[node.feature] <= node.threshold:
            return self._traverse_tree(x, node.left)
        return self._traverse_tree(x, node.right)

    def predict(self, X):
        return np.array([self._traverse_tree(x, self.root) for x in X])
```
* **Note:** Feature scaling is **NOT** needed for Decision Trees because splits depend only on threshold comparisons ($x_j \le t$). Evaluation uses 5-Fold CV.

---

## LAB 13 (PA9): Perceptron (OR/NAND), Categorical Naive Bayes & Gaussian Naive Bayes

**Files Read:** `LAB13/answer1.py`, `LAB13/PA9_CS32.pdf`  
**Important Note:** Implemented in **pure Python** (`import math, random`) without any external ML packages!

### Question 1: Perceptron Classification (OR & NAND Gates)

#### Stage 1: Imports & Activation Function
```python
import math
import random

def step_function(z):
    return 1 if z >= 0 else 0
```

#### Stage 2: Data Preparation (80:20 Split) & Training (2 Epochs)
```python
def run_perceptron(gate_name, raw_data, epochs=2, lr=0.1, seed=42):
    random.seed(seed)
    data = raw_data * 5                  # Replicate 4 rows -> 20 samples for clean 16:4 split
    random.shuffle(data)

    split_idx = int(0.8 * len(data))
    train_data = data[:split_idx]
    test_data = data[split_idx:]

    # Random initialization of weights & bias
    w = [random.uniform(-0.5, 0.5) for _ in range(len(raw_data[0][0]))]
    b = random.uniform(-0.5, 0.5)

    # Perceptron Learning Rule
    for epoch in range(epochs):
        for x, y in train_data:
            z = sum(wi * xi for wi, xi in zip(w, x)) + b
            y_hat = step_function(z)
            err = y - y_hat
            w = [wi + lr * err * xi for wi, xi in zip(w, x)]
            b = b + lr * err

    # Predict & evaluate class-wise accuracy, precision, recall for train & test
    train_pred = [step_function(sum(wi * xi for wi, xi in zip(w, x)) + b) for x, _ in train_data]
    test_pred  = [step_function(sum(wi * xi for wi, xi in zip(w, x)) + b) for x, _ in test_data]

or_gate = [([0, 0], 0), ([0, 1], 1), ([1, 0], 1), ([1, 1], 1)]
nand_gate = [([0, 0], 1), ([0, 1], 1), ([1, 0], 1), ([1, 1], 0)]
```
* **Perceptron Weight Update Formula:**
  $$w_i \leftarrow w_i + \eta (y - \hat{y}) x_i, \qquad b \leftarrow b + \eta (y - \hat{y})$$
  (where $\hat{y} = 1$ if $w \cdot x + b \ge 0$ else $0$).

---

### Question 2: Categorical Naive Bayes (E-Commerce Purchase Prediction)

#### Stage 1: Dataset Definition
```python
# Columns: (Age, Income, BrowsingTime, PrevPurchase, Target_Purchase)
dataset_q2 = [
    ("Young", "High", "long", "No", "No"),
    ("Young", "High", "long", "Yes", "No"),
    ("Middle", "High", "long", "No", "Yes"),
    ("Senior", "Medium", "long", "No", "Yes"),
    ("Senior", "Low", "short", "No", "Yes"),
    ("Senior", "Low", "short", "Yes", "No"),
    ("Middle", "Low", "short", "Yes", "Yes"),
    ("Young", "Medium", "long", "No", "No"),
    ("Young", "Low", "short", "No", "Yes"),
    ("Senior", "Medium", "short", "No", "Yes"),
    ("Young", "Medium", "short", "Yes", "Yes"),
    ("Middle", "Medium", "long", "Yes", "Yes"),
    ("Middle", "High", "short", "No", "Yes"),
    ("Senior", "Medium", "long", "Yes", "No"),
]
```

#### Stage 2: Categorical Naive Bayes Class (with Laplace Smoothing)
```python
class CategoricalNaiveBayes:
    def __init__(self, laplace=1.0):
        self.laplace = laplace

    def fit(self, X, y):
        self.classes = sorted(list(set(y)))
        n_samples = len(y)
        n_features = len(X[0])
        self.vocab = {i: set(row[i] for row in X) for i in range(n_features)}

        self.priors = {}
        self.likelihoods = {c: {i: {} for i in range(n_features)} for c in self.classes}

        for c in self.classes:
            c_indices = [idx for idx, target in enumerate(y) if target == c]
            count_c = len(c_indices)
            self.priors[c] = count_c / n_samples

            for i in range(n_features):
                vals_in_c = [X[idx][i] for idx in c_indices]
                v_k = len(self.vocab[i])
                for v in self.vocab[i]:
                    # Laplace Smoothing prevents zero probability
                    self.likelihoods[c][i][v] = (vals_in_c.count(v) + self.laplace) / (count_c + self.laplace * v_k)

    def predict_proba(self, x):
        posteriors = {}
        for c in self.classes:
            prob = self.priors[c]
            for i, val in enumerate(x):
                prob *= self.likelihoods[c][i].get(val, 1.0 / (len(self.vocab[i]) + 1))
            posteriors[c] = prob
        total = sum(posteriors.values())
        return {c: posteriors[c] / total for c in self.classes}

    def predict(self, X):
        return [max(self.predict_proba(x), key=self.predict_proba(x).get) for x in X]
```
* **Formula (with Laplace Smoothing $\alpha = 1$):**
  $$P(C \mid x) \propto P(C) \prod_{i=1}^n P(x_i \mid C), \qquad P(x_i = v \mid C) = \frac{\text{count}(x_i=v, C) + \alpha}{N_C + \alpha |V_i|}$$
* **Test Query:** `("Middle", "High", "long", "Yes")` $\to$ Predicts `Yes`.

---

### Question 3: Gaussian Naive Bayes (Continuous Diabetes Dataset)

#### Stage 1: Gaussian Naive Bayes Class
```python
class GaussianNaiveBayes:
    def _mean(self, nums):
        return sum(nums) / len(nums)

    def _stdev(self, nums):
        avg = self._mean(nums)
        var = sum((x - avg) ** 2 for x in nums) / (len(nums) - 1)  # Sample variance (N-1)
        return math.sqrt(var)

    def _gaussian_density(self, x, mean, stdev):
        if stdev == 0:
            return 1.0 if x == mean else 0.0
        exponent = math.exp(-((x - mean) ** 2) / (2 * (stdev ** 2)))
        return (1 / (math.sqrt(2 * math.pi) * stdev)) * exponent

    def fit(self, dataset):
        self.classes = sorted(list(set(row[-1] for row in dataset)))
        separated = {c: [row[:-1] for row in dataset if row[-1] == c] for c in self.classes}
        n_samples = len(dataset)

        self.priors = {c: len(separated[c]) / n_samples for c in self.classes}
        self.stats = {}
        for c in self.classes:
            columns = zip(*separated[c])   # Transpose rows -> feature columns
            self.stats[c] = [(self._mean(col), self._stdev(col)) for col in columns]

    def predict_proba(self, x):
        posteriors = {}
        for c in self.classes:
            log_prob = math.log(self.priors[c])
            for i, (m, s) in enumerate(self.stats[c]):
                density = self._gaussian_density(x[i], m, s)
                log_prob += math.log(max(density, 1e-12))
            posteriors[c] = log_prob

        # Log-sum-exp trick to convert log probabilities back to normalized probabilities safely
        max_log = max(posteriors.values())
        exp_p = {c: math.exp(v - max_log) for c, v in posteriors.items()}
        sum_exp = sum(exp_p.values())
        return {c: exp_p[c] / sum_exp for c in self.classes}

    def predict(self, X):
        return [max(self.predict_proba(x), key=self.predict_proba(x).get) for x in X]
```
* **Gaussian PDF Formula:**
  $$P(x_i \mid C) = \frac{1}{\sqrt{2\pi}\,\sigma_{i,C}} \exp\!\left(-\frac{(x_i - \mu_{i,C})^2}{2\sigma_{i,C}^2}\right)$$
* **Comparison (Q2 Categorical NB vs Q3 Gaussian NB):**
  * **Categorical NB** estimates discrete frequency probabilities using counts + Laplace smoothing (best for nominal/categorical features like `Young/Middle/Senior`).
  * **Gaussian NB** assumes continuous features follow a Normal distribution $\mathcal{N}(\mu, \sigma^2)$ per class and computes PDF values (best for continuous features like `Glucose, BMI, Age`), using `log` probabilities to prevent floating-point underflow.

---

## Final Quick-Revision Formula & Exam Cheat Sheet

| Lab | Algorithm | Scaling Needed? | Splitting / Validation | Key Update / Core Formula |
| :--- | :--- | :--- | :--- | :--- |
| **LAB7** | Binary Logistic Regression (Batch GD) | **Yes** (Z-score) | 80:20 (+10% Val) & 5-Fold CV | $w \leftarrow w - \frac{\alpha}{m} X^T (\sigma(Xw) - y)$ |
| **LAB8 P1** | Multi-Class Logistic (One-vs-All) | **Yes** (Z-score) | 5-Fold CV (+10% Val) | Train $K$ binary models `(y == c)`; $\hat{y} = \arg\max_c \sigma(X w_c)$ |
| **LAB8 P2** | K-Means + PCA | **Yes** (Z-score) | Unsupervised | Assign $\arg\min_k \|x - \mu_k\|$; update $\mu_k = \text{mean}(C_k)$; PCA via `np.cov` + `np.linalg.eig` |
| **LAB9** | Binary Logistic Regression (SGD) | **Compare No vs Yes** | 5-Fold CV (fit scaler on train only!) | Per sample $i$: $\theta \leftarrow \theta - \alpha (h_i - y_i) x_i$ |
| **LAB10** | DBSCAN + Hierarchical (Scratch) | Optional/Distance | Grid Search + K-Dist Elbow | Region query $\|x_i - x_j\| \le \varepsilon$; Linkage: `min` (single), `max` (complete), centroid |
| **LAB11** | DBSCAN (`sklearn`) | **Yes** (`StandardScaler`) | Unsupervised | `DBSCAN(eps, min_samples).fit_predict(X)`; filter `labels != -1` for `silhouette_score` |
| **LAB12 P1** | Standard & Weighted K-NN | **Yes** (Z-score) | 5-Fold CV | Top-$K$ smallest $\|x_{\text{train}} - x\|$; Weighted: $w_i = \frac{1}{d_i + \epsilon}$ |
| **LAB12 P2** | Continuous ID3 Decision Tree | **No** | 5-Fold CV | $IG = H(S) - \sum \frac{\|S_v\|}{\|S\|} H(S_v)$; thresholds via `np.percentile` |
| **LAB13 Q1** | Perceptron (OR / NAND) | No (Binary 0/1) | 80:20 Split (2 epochs) | $w \leftarrow w + \eta(y - \hat{y})x$, $\hat{y} = 1[w\cdot x + b \ge 0]$ |
| **LAB13 Q2** | Categorical Naive Bayes | No | Full / Test Query | $P(v \mid C) = \frac{\text{count}(v,C)+\alpha}{N_C + \alpha \|V\|}$ |
| **LAB13 Q3** | Gaussian Naive Bayes | No | Full / Test Query | $\frac{1}{\sqrt{2\pi}\sigma} e^{-(x-\mu)^2/(2\sigma^2)}$; log-sum-exp normalization |

### Evaluation Metric Formulas (Guaranteed Exam Questions!)
* $\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$
* $\text{Class-1 Accuracy (Recall / Sensitivity)} = \frac{TP}{TP + FN}$
* $\text{Class-0 Accuracy (Specificity)} = \frac{TN}{TN + FP}$
* $\text{Precision} = \frac{TP}{TP + FP}$
* $\text{F1-Score} = \frac{2 \times \text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$
* $\text{Silhouette Score } s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$

Good luck on your ML lab exam today!


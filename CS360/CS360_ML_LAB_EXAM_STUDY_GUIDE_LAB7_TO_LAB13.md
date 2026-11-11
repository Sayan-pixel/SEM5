# CS360 Machine Learning Lab — Complete Pen-and-Paper Exam Study Guide (LAB7 to LAB13)

> **How This Guide Is Structured:** Prepared strictly from `LAB7` through `LAB13` in `CS360` for **pen-and-paper lab exams** (no IDE, no laptop). Every stage and every algorithm shows **BOTH** the **From-Scratch (Custom)** code AND the **Built-in Library (`sklearn` / `scipy`)** equivalent **side-by-side in the same section**, so you can compare them directly and write whichever version your exam asks for!

---

## Table of Contents

1. [Part 0: Universal ML Program Structure (Custom vs Built-In)](#part-0-universal-ml-program-structure-custom-vs-built-in)
2. [LAB 7 (PA5): Binary Logistic Regression (Batch GD), Decision Thresholds & 5-Fold CV](#lab-7-pa5-binary-logistic-regression-batch-gd-decision-thresholds--5-fold-cv)
3. [LAB 8 (PA6): Multi-Class Logistic Regression (One-vs-All) & K-Means Clustering + PCA](#lab-8-pa6-multi-class-logistic-regression-one-vs-all--k-means-clustering--pca)
4. [LAB 9 (EA2): Binary Logistic Regression via SGD, Feature Scaling & Feature Subsets](#lab-9-ea2-binary-logistic-regression-via-sgd-feature-scaling--feature-subsets)
5. [LAB 10 (PA7): DBSCAN (Grid Search + K-Distance Elbow) & Hierarchical Clustering](#lab-10-pa7-dbscan-grid-search--k-distance-elbow--hierarchical-clustering)
6. [LAB 11 (EA3): DBSCAN on Air Quality with Standardization & Silhouette Score](#lab-11-ea3-dbscan-on-air-quality-with-standardization--silhouette-score)
7. [LAB 12 (PA8): Standard vs Weighted K-NN & Continuous-Attribute ID3 Decision Tree](#lab-12-pa8-standard-vs-weighted-k-nn--continuous-attribute-id3-decision-tree)
8. [LAB 13 (PA9): Perceptron (OR/NAND), Categorical Naive Bayes & Gaussian Naive Bayes](#lab-13-pa9-perceptron-ornand-categorical-naive-bayes--gaussian-naive-bayes)
9. [Master Built-In Imports & Final Exam Cheat Sheet](#master-built-in-imports--final-exam-cheat-sheet)

---

## Part 0: Universal ML Program Structure (Custom vs Built-In)

Every ML lab program in CS360 follows the same **8 standard stages**. Memorize these shared building blocks first, and then plug in each lab's algorithm!

### Stage 0.1: Importing Libraries (Base vs Built-In ML)

```python
# --- Core Libraries (Needed in BOTH Custom and Built-In programs) ---
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Built-In ML Libraries (Use when in-built packages ARE allowed) ---
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.linear_model import LogisticRegression, SGDClassifier, Perceptron
from sklearn.multiclass import OneVsRestClassifier
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier, NearestNeighbors
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import CategoricalNB, GaussianNB
from sklearn.metrics import (
    confusion_matrix, accuracy_score, precision_score,
    recall_score, f1_score, classification_report, silhouette_score
)
from scipy.cluster.hierarchy import linkage, dendrogram
```

| Library | Alias / Module | Purpose in CS360 Labs |
| :--- | :--- | :--- |
| **NumPy** | `np` | Arrays, matrix math (`np.dot`, `np.linalg.norm`), math (`np.exp`, `np.log`), random sampling/shuffling. |
| **Pandas** | `pd` | Reading CSVs (`pd.read_csv`), one-hot encoding (`pd.get_dummies`), selecting/dropping columns, Excel export. |
| **Matplotlib** | `plt` | Scatter plots, K-distance curves, subplots (`plt.subplots`), saving figures (`plt.savefig`). |
| **Seaborn** | `sns` | Confusion Matrix heatmaps (`sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')`). |
| **Scikit-learn** | `sklearn` | Pre-built splitting, scaling, ML models, and evaluation metrics. |
| **SciPy** | `scipy.cluster.hierarchy` | Hierarchical `linkage()` matrix computation and `dendrogram()` plotting. |
| **Built-in Python** | `math`, `random` | Used in LAB13 pure-Python implementations without NumPy/Pandas. |

---

### Stage 0.2: Common Preprocessing (Z-Score Standardization & Bias Term)

#### A. Z-Score Standardization: $X_{\text{scaled}} = \frac{X - \mu}{\sigma}$

```python
# ==================== FROM SCRATCH (NumPy) ====================
mean = np.mean(X_train, axis=0)
std = np.std(X_train, axis=0)
std[std == 0] = 1.0                       # Prevent division by zero
X_train_scaled = (X_train - mean) / std
X_test_scaled  = (X_test - mean) / std    # Always use TRAIN mean & std on test!

# ==================== USING BUILT-IN (Scikit-Learn) ====================
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
```
* **Why needed?** Prevents large-scale features (`balance = 100,000`, `PM10 = 150`) from dominating gradient updates or Euclidean distances.
* **Data Leakage Rule:** Always compute `mean` / `std` (or call `.fit()`) **ONLY on training data**, then transform validation/test data.

#### B. Bias / Intercept Column ($x_0 = 1$)
```python
# ==================== FROM SCRATCH (NumPy) ====================
X_train_bias = np.hstack((np.ones((X_train.shape[0], 1)), X_train))
# OR: X_bias = np.c_[np.ones(X.shape[0]), X]

# ==================== USING BUILT-IN (Scikit-Learn) ====================
# Do NOT add a column of 1s! sklearn models have fit_intercept=True by default.
# If X already has a bias column at index 0, pass X[:, 1:] to sklearn.
```

---

### Stage 0.3: Data Splitting & 5-Fold Cross-Validation

#### A. Random 80:20 Train-Test Split (+ 10% Validation Split)
```python
# ==================== FROM SCRATCH (NumPy) ====================
def custom_train_test_split(X, y, test_size=0.2, random_state=42):
    np.random.seed(random_state)
    indices = np.random.permutation(len(X))
    test_samples = int(len(X) * test_size)
    test_idx = indices[:test_samples]
    train_idx = indices[test_samples:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]

X_train_full, X_test, y_train_full, y_test = custom_train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = custom_train_test_split(X_train_full, y_train_full, test_size=0.1, random_state=42)

# ==================== USING BUILT-IN (Scikit-Learn) ====================
from sklearn.model_selection import train_test_split

X_train_full, X_test, y_train_full, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X_train_full, y_train_full, test_size=0.1, random_state=42)
```

#### B. 5-Fold Cross-Validation ($K = 5$)
```python
# ==================== FROM SCRATCH (NumPy) ====================
np.random.seed(42)
indices = np.arange(len(X))
np.random.shuffle(indices)
folds = np.array_split(indices, 5)

for i in range(5):
    test_idx = folds[i]
    train_idx = np.hstack([folds[j] for j in range(5) if j != i])
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test   = X[test_idx], y[test_idx]

# ==================== USING BUILT-IN (Scikit-Learn) ====================
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)
for train_idx, test_idx in kf.split(X):
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test   = X[test_idx], y[test_idx]
```

---

### Stage 0.4: Classification Evaluation Metrics & Confusion Matrix

#### A. Binary Classification Metrics
```python
# ==================== FROM SCRATCH (NumPy) ====================
def evaluate_binary(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    cm = np.array([[tn, fp], [fn, tp]])

    accuracy    = (tp + tn) / len(y_true)
    class_0_acc = tn / (tn + fp) if (tn + fp) > 0 else 0.0   # Specificity
    class_1_acc = tp / (tp + fn) if (tp + fn) > 0 else 0.0   # Recall / Sensitivity
    precision   = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall      = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    return cm, accuracy, class_0_acc, class_1_acc, precision, recall

# ==================== USING BUILT-IN (Scikit-Learn) ====================
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score

cm   = confusion_matrix(y_true, y_pred)
acc  = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, zero_division=0)
rec  = recall_score(y_true, y_pred, zero_division=0)
tn, fp, fn, tp = cm.ravel()
class_0_acc = tn / (tn + fp)
class_1_acc = tp / (tp + fn)
```

#### B. Multi-Class Confusion Matrix & Per-Class Metrics (Used in LAB8, LAB12, LAB13)
```python
# ==================== FROM SCRATCH (NumPy) ====================
def get_confusion_matrix(y_true, y_pred, num_classes):
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm

def calculate_metrics(cm):
    total = np.sum(cm)
    overall_acc = np.trace(cm) / total if total > 0 else 0.0
    class_acc, precision, recall = [], [], []
    for i in range(cm.shape[0]):
        tp = cm[i, i]
        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp
        tn = total - tp - fp - fn
        class_acc.append((tp + tn) / total)
        precision.append(tp / (tp + fp) if (tp + fp) > 0 else 0.0)
        recall.append(tp / (tp + fn) if (tp + fn) > 0 else 0.0)
    return overall_acc, class_acc, precision, recall

# ==================== USING BUILT-IN (Scikit-Learn) ====================
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, classification_report

cm = confusion_matrix(y_true, y_pred)
overall_acc = accuracy_score(y_true, y_pred)
precision_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
recall_per_class    = recall_score(y_true, y_pred, average=None, zero_division=0)
print(classification_report(y_true, y_pred, zero_division=0))
```

---

## LAB 7 (PA5): Binary Logistic Regression (Batch GD), Decision Thresholds & 5-Fold CV

**Files Read:** `LAB7/2401179_PA5.py`, `LAB7/run_lab7_experiments.py`, `LAB7/PA5_CS32.pdf`  
**Task:** Classify diabetic vs non-diabetic patients (`diabetes_prediction_dataset.csv`), tune `(alpha, rho, epochs)`, compare custom Batch GD vs `sklearn`, evaluate thresholds `{0.3, 0.5, 0.7}`, and run 5-Fold CV.

### Stage 1: Imports & Data Preprocessing (One-Hot Encoding + Scaling)
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score

df = pd.read_csv("diabetes_prediction_dataset.csv")
df = pd.get_dummies(df, columns=['gender', 'smoking_history'], drop_first=True)

X = df.drop('diabetes', axis=1).astype(float).values
y = df['diabetes'].values.astype(int)
```
* **`pd.get_dummies(..., drop_first=True)`:** Encodes categorical strings into $0/1$ columns and drops one category per feature to avoid dummy variable multicollinearity.

### Stage 2: Split & Standardize (Custom vs Built-In)
```python
# ==================== FROM SCRATCH ====================
mean, std = np.mean(X, axis=0), np.std(X, axis=0)
std[std == 0] = 1.0
X_scaled = (X - mean) / std
X_design = np.c_[np.ones(X_scaled.shape[0]), X_scaled]   # Add bias x0 = 1

X_train_full, X_test, y_train_full, y_test = custom_train_test_split(X_design, y, test_size=0.2, random_state=42)
X_train, X_val, y_train, y_val = custom_train_test_split(X_train_full, y_train_full, test_size=0.1, random_state=42)

# ==================== USING BUILT-IN ====================
X_train_full, X_test, y_train_full, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train_full)
X_test_s  = scaler.transform(X_test)
```

### Stage 3: Binary Logistic Regression Model (Custom Batch GD vs Built-In)

#### Option A: From Scratch (Batch Gradient Descent)
```python
class CustomLogisticRegression:
    def __init__(self, alpha=0.01, rho=0.001, epochs=100, threshold=0.5):
        self.alpha, self.rho, self.epochs, self.threshold = alpha, rho, epochs, threshold
        self.w = None

    def sigmoid(self, z):
        z = np.clip(z, -250, 250)                 # Prevents exp() overflow
        return 1.0 / (1.0 + np.exp(-z))

    def compute_loss(self, y, y_pred):
        m = len(y)
        y_pred = np.clip(y_pred, 1e-15, 1.0 - 1e-15)  # Prevents log(0)
        return -(1.0 / m) * np.sum(y * np.log(y_pred) + (1.0 - y) * np.log(1.0 - y_pred))

    def fit(self, X, y):
        m, n = X.shape
        self.w = np.zeros(n)                      # Initialize weights to zero
        loss_history = []
        for epoch in range(self.epochs):
            y_pred = self.sigmoid(np.dot(X, self.w))
            loss = self.compute_loss(y, y_pred)
            if len(loss_history) > 0 and abs(loss_history[-1] - loss) <= self.rho:
                break                             # Stopping criterion: |loss_prev - loss| <= rho
            loss_history.append(loss)
            gradient = np.dot(X.T, (y_pred - y)) / m
            self.w -= self.alpha * gradient

    def predict_proba(self, X):
        return self.sigmoid(np.dot(X, self.w))

    def predict(self, X, threshold=None):
        t = self.threshold if threshold is None else threshold
        return (self.predict_proba(X) >= t).astype(int)
```
* **Formulas:**
  * Hypothesis: $\hat{y} = \sigma(Xw) = \frac{1}{1+e^{-Xw}}$
  * Gradient (Batch GD): $\nabla J(w) = \frac{1}{m} X^T (\hat{y} - y)$, Update: $w \leftarrow w - \alpha \nabla J(w)$

#### Option B: Using Built-In (`sklearn.linear_model.LogisticRegression`)
```python
builtin_model = LogisticRegression(max_iter=100)
builtin_model.fit(X_train_s, y_train_full)

# Default prediction (threshold = 0.5):
y_pred_05 = builtin_model.predict(X_test_s)

# Custom threshold predictions using .predict_proba(X)[:, 1]:
probs = builtin_model.predict_proba(X_test_s)[:, 1]
y_pred_03 = (probs >= 0.3).astype(int)
y_pred_07 = (probs >= 0.7).astype(int)
```

### Stage 4: Hyperparameter Tuning & Threshold Comparison Plot
```python
# Grid search on validation set (for custom model)
alphas, rhos, epochs_list = [0.0001, 0.1], [0.001, 0.01], [50, 100]
best_val_acc, best_params = -1.0, {}
for alpha in alphas:
    for rho in rhos:
        for epochs in epochs_list:
            model = CustomLogisticRegression(alpha=alpha, rho=rho, epochs=epochs)
            model.fit(X_train, y_train)
            val_acc = np.mean(model.predict(X_val) == y_val)
            if val_acc > best_val_acc:
                best_val_acc, best_params = val_acc, {'alpha': alpha, 'rho': rho, 'epochs': epochs}

best_model = CustomLogisticRegression(**best_params)
best_model.fit(X_train_full, y_train_full)

# Plot confusion matrices at thresholds 0.3, 0.5, 0.7
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for idx, thresh in enumerate([0.3, 0.5, 0.7]):
    y_p = best_model.predict(X_test, threshold=thresh)
    cm, acc, c0, c1, prec, rec = evaluate_binary(y_test, y_p)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[idx], cbar=False)
    axes[idx].set_title(f"Threshold = {thresh}")
plt.tight_layout()
plt.savefig("Combined_Confusion_Matrices.png")
```

### Stage 5: Key Exam Observations (LAB7)
1. **Threshold Trade-off (`0.3` $\to$ `0.5` $\to$ `0.7`):** Lowering threshold (`0.3`) predicts positive aggressively $\implies$ **FP rises, FN drops $\implies$ High Recall, Low Precision**. Raising threshold (`0.7`) makes positive predictions strict $\implies$ **FP drops, FN rises $\implies$ High Precision, Low Recall**.
2. **80:20 Split vs 5-Fold CV:** On $N=100{,}000$, accuracy is nearly identical, but 5-Fold CV evaluates every sample once as test data, giving lower variance and a more reliable generalization estimate.

---

## LAB 8 (PA6): Multi-Class Logistic Regression (One-vs-All) & K-Means Clustering + PCA

**Files Read:** `LAB8/Problem1.py`, `LAB8/Problem2.py`, `LAB8/run_lab8_experiments.py`, `LAB8/PA6_CS32.pdf`

### Problem 1: Multi-Class Logistic Regression (One-vs-All) on `Iris.csv`

#### Stage 1: Load & Encode Labels (Custom vs Built-In)
```python
df = pd.read_csv('Iris.csv')
X_raw = df[['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm']].values
y_labels = df['Species'].values

# ==================== FROM SCRATCH ====================
classes = np.unique(y_labels)
label_to_idx = {label: idx for idx, label in enumerate(classes)}
y = np.array([label_to_idx[lbl] for lbl in y_labels])
X_scaled = (X_raw - np.mean(X_raw, axis=0)) / np.std(X_raw, axis=0)
X = np.hstack((np.ones((X_scaled.shape[0], 1)), X_scaled))  # Bias column

# ==================== USING BUILT-IN ====================
from sklearn.preprocessing import LabelEncoder, StandardScaler
y = LabelEncoder().fit_transform(y_labels)
# Scaling is done inside each KFold using StandardScaler()
```

#### Stage 2: One-vs-All Multi-Class Logistic Regression (Custom vs Built-In)

##### Option A: From Scratch (One-vs-All Batch GD)
```python
def batch_gradient_descent(X, y, alpha, rho, max_epochs):
    m, n = X.shape
    theta = np.zeros(n)
    cost_history = []
    for epoch in range(max_epochs):
        h = sigmoid(X.dot(theta))
        theta = theta - alpha * (1.0 / m) * X.T.dot(h - y)
        cost = compute_cost(X, y, theta)
        cost_history.append(cost)
        if epoch > 0 and abs(cost_history[-2] - cost_history[-1]) <= rho:
            break
    return theta

def train_one_vs_all(X, y, alpha, rho, max_epochs, num_classes):
    thetas = []
    for c in range(num_classes):
        y_binary = (y == c).astype(int)       # Class c vs all others
        thetas.append(batch_gradient_descent(X, y_binary, alpha, rho, max_epochs))
    return np.array(thetas)                   # Shape: (K, n_features)

def predict_one_vs_all(X, thetas):
    probs = sigmoid(X.dot(thetas.T))          # Shape: (N, K)
    return np.argmax(probs, axis=1)           # Highest probability class
```

##### Option B: Using Built-In (`OneVsRestClassifier` + `LogisticRegression`)
```python
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)
for fold, (train_idx, test_idx) in enumerate(kf.split(X_raw), start=1):
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(X_raw[train_idx])
    X_te = scaler.transform(X_raw[test_idx])

    model = OneVsRestClassifier(LogisticRegression(max_iter=100))
    model.fit(X_tr, y[train_idx])
    y_pred = model.predict(X_te)
    cm = confusion_matrix(y[test_idx], y_pred)
```

#### Stage 3: Export Results to Multi-Sheet Excel
```python
with pd.ExcelWriter('Problem1_Results.xlsx') as writer:
    df_all_folds.to_excel(writer, sheet_name='All Folds Metrics', index=False)
    df_avg.to_excel(writer, sheet_name='Average Metrics', index=False)
    df_best.to_excel(writer, sheet_name='Best Fold Metrics', index=False)
```

---

### Problem 2: Unsupervised K-Means Clustering + PCA on `WineQT.csv`

#### Stage 1: Load Unlabeled Features & Standardize
```python
df = pd.read_csv('WineQT.csv')
drop_cols = [c for c in ['Id', 'quality'] if c in df.columns]
X = df.drop(columns=drop_cols).values.astype(float)

# Standardize (Custom vs Built-In)
X_scaled = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
# OR: X_scaled = StandardScaler().fit_transform(X)
```

#### Stage 2: K-Means Clustering & PCA Visualization (Custom vs Built-In)

##### Option A: From Scratch (K-Means + Custom PCA)
```python
def k_means(X, K, max_iters=1000):
    n_samples = X.shape[0]
    centroids = X[np.random.choice(n_samples, K, replace=False)].copy()
    assignments = np.zeros(n_samples, dtype=int)

    for epoch in range(max_iters):
        distances = np.linalg.norm(X[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
        new_assignments = np.argmin(distances, axis=1)
        if np.array_equal(assignments, new_assignments):
            break                                 # Stopping criterion: no change
        assignments = new_assignments
        for k in range(K):
            pts = X[assignments == k]
            if len(pts) > 0:
                centroids[k] = np.mean(pts, axis=0)
    return assignments, centroids

def get_first_two_pcs(X):
    cov_matrix = np.cov(X.T)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
    top_2 = eigenvectors[:, np.argsort(eigenvalues)[::-1][:2]]
    return np.real(np.dot(X, top_2))
```

##### Option B: Using Built-In (`KMeans` + `PCA`)
```python
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

X_pca = PCA(n_components=2).fit_transform(X_scaled)

fig, axes = plt.subplots(2, 2, figsize=(15, 10))
for ax, K in zip(axes.flatten(), [3, 5, 10, 15]):
    kmeans = KMeans(n_clusters=K, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    ax.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='tab10', s=20, alpha=0.6)
    ax.set_title(f"K-Means (K={K}) | Inertia={kmeans.inertia_:.1f}")
plt.tight_layout()
plt.show()
```
* **Key Observation (LAB8 P2):** As $K$ rises ($3 \to 5 \to 10 \to 15$), inertia (WCSS) decreases monotonically, but clusters become small, fragmented, and overlap in 2D PCA space.

---

## LAB 9 (EA2): Binary Logistic Regression via SGD, Feature Scaling & Feature Subsets

**Files Read:** `LAB9/2401179_problem1.py`, `LAB9/run_lab9_experiments.py`, `LAB9/EA2_CS32.pdf`  
**Task:** Generate 500 synthetic fraud transactions across 5 vastly different feature scales, train **SGD Logistic Regression** in 5-Fold CV **without scaling (1b)** vs **with Z-score scaling (1c)**, and compare **Model A (2 features)** vs **Model B (all 5 features)**.

### Stage 1: Generate Synthetic Dataset
```python
np.random.seed(42)
n_samples = 500
amount             = np.random.uniform(10, 10000, n_samples)
balance            = np.random.uniform(100, 100000, n_samples)
total_transactions = np.random.randint(1, 5000, n_samples)
frequency          = np.random.uniform(0.1, 30, n_samples)
time_since_last    = np.random.uniform(0, 365, n_samples)

z = (0.001 * amount - 0.0001 * balance + 0.005 * total_transactions
     + 0.5 * frequency - 0.02 * time_since_last)
y = (1 / (1 + np.exp(-np.clip(z, -250, 250))) > 0.5).astype(int)
X_all = np.column_stack((amount, balance, total_transactions, frequency, time_since_last))
```

### Stage 2: SGD Logistic Regression inside 5-Fold CV (Custom vs Built-In)

#### Option A: From Scratch (SGD + Manual 5-Fold + Manual Scaler)
```python
def sgd_logistic_regression(X, y, alpha=0.01, rho=0.001, max_epochs=500):
    m, n = X.shape
    theta = np.zeros(n)
    cost_history = []
    for epoch in range(max_epochs):
        indices = np.arange(m)
        np.random.shuffle(indices)
        X_shuf, y_shuf = X[indices], y[indices]

        for i in range(m):                        # Update ONCE PER SAMPLE
            xi, yi = X_shuf[i], y_shuf[i]
            hi = sigmoid(np.dot(xi, theta))
            theta = theta - alpha * xi * (hi - yi)

        cost = compute_cost(X, y, theta)
        cost_history.append(cost)
        if epoch > 0 and abs(cost_history[-2] - cost_history[-1]) < rho:
            break
    return theta

def k_fold_cv_scratch(X, y, k=5, alpha=0.01, rho=0.001, normalize=False):
    indices = np.arange(len(X))
    np.random.shuffle(indices)
    folds = np.array_split(indices, k)
    metrics = []
    for i in range(k):
        test_idx = folds[i]
        train_idx = np.hstack([folds[j] for j in range(k) if j != i])
        X_tr, y_tr = X[train_idx], y[train_idx]
        X_te, y_te = X[test_idx], y[test_idx]
        if normalize:
            mean, std = np.mean(X_tr, axis=0), np.std(X_tr, axis=0)
            std[std == 0] = 1.0
            X_tr, X_te = (X_tr - mean) / std, (X_te - mean) / std
        X_tr = np.hstack((np.ones((len(X_tr), 1)), X_tr))
        X_te = np.hstack((np.ones((len(X_te), 1)), X_te))
        theta = sgd_logistic_regression(X_tr, y_tr, alpha, rho)
        y_pred = (sigmoid(X_te.dot(theta)) >= 0.5).astype(int)
        metrics.append(evaluate_binary(y_te, y_pred))
    return metrics
```

#### Option B: Using Built-In (`SGDClassifier(loss='log_loss')` + `KFold` + `StandardScaler`)
```python
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

def k_fold_cv_builtin(X, y, k=5, normalize=False):
    kf = KFold(n_splits=k, shuffle=True, random_state=42)
    metrics = []
    for train_idx, test_idx in kf.split(X):
        X_tr, X_te = X[train_idx], X[test_idx]
        y_tr, y_te = y[train_idx], y[test_idx]

        if normalize:
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_tr)
            X_te = scaler.transform(X_te)

        sgd = SGDClassifier(loss='log_loss', learning_rate='constant',
                            eta0=0.01, tol=0.001, max_iter=500, random_state=42)
        sgd.fit(X_tr, y_tr)
        y_pred = sgd.predict(X_te)
        metrics.append((accuracy_score(y_te, y_pred), precision_score(y_te, y_pred, zero_division=0)))
    return metrics
```

### Stage 3: Running the 4 Experiments & Observations
```python
# 1(b) Without scaling:        k_fold_cv(X_all, y, normalize=False)
# 1(c) With Z-score scaling:   k_fold_cv(X_all, y, normalize=True)
# 1(e) Model A (2 features):   k_fold_cv(X_all[:, [0, 3]], y, normalize=True)
# 1(e) Model B (all features): k_fold_cv(X_all, y, normalize=True)
```
* **Key Observations (LAB9):**
  1. **Unscaled vs Scaled:** Without scaling, `account_balance` ($\le 100{,}000$) and `amount` ($\le 10{,}000$) blow up SGD gradients and saturate `sigmoid`, making the model predict only Fraud (Non-Fraud accuracy $\approx 0\%$). Z-score scaling restores spherical contours and boosts Non-Fraud detection.
  2. **Model A vs Model B:** Model B (all 5 predictors) outperforms Model A (only `amount` & `frequency`) because `balance`, `total_transactions`, and `time_since_last` are required to separate non-fraud cases.

---

## LAB 10 (PA7): DBSCAN (Grid Search + K-Distance Elbow) & Hierarchical Clustering

**Files Read:** `LAB10/answer.py`, `LAB10/PA7_CS32.pdf`  
**Task:** Cluster `Mall_Customers.csv` (`Annual Income (k$)` and `Spending Score (1-100)`) using DBSCAN (Grid Search + K-Distance graph) and Hierarchical Clustering (`single`, `complete`, `centroid` linkage + dendrogram).

### Stage 1: Load Data
```python
df = pd.read_csv("Mall_Customers.csv")
X = df.iloc[:, [3, 4]].values
```

### Stage 2: DBSCAN & Grid Search (Custom vs Built-In)

#### Option A: From Scratch (`dbscan_scratch` + `silhouette_score_scratch`)
```python
def euclidean_distance(p1, p2):
    return np.sqrt(np.sum((p1 - p2) ** 2))

def region_query(X, point_idx, eps):
    return [i for i in range(len(X)) if euclidean_distance(X[point_idx], X[i]) <= eps]

def dbscan_scratch(X, eps, minpts):
    labels = np.full(len(X), 0)   # 0 = unvisited, -1 = noise, >0 = cluster
    cluster_id = 0
    for i in range(len(X)):
        if labels[i] != 0:
            continue
        neighbors = region_query(X, i, eps)
        if len(neighbors) < minpts:
            labels[i] = -1
        else:
            cluster_id += 1
            labels[i] = cluster_id
            queue = [n for n in neighbors if n != i]
            while queue:
                q_point = queue.pop(0)
                if labels[q_point] == -1:
                    labels[q_point] = cluster_id          # Border point
                if labels[q_point] == 0:
                    labels[q_point] = cluster_id
                    q_neighbors = region_query(X, q_point, eps)
                    if len(q_neighbors) >= minpts:        # Core point
                        queue.extend(q_neighbors)
    return labels

def silhouette_score_scratch(X, labels):
    unique_labels = np.unique(labels)
    if len(unique_labels) <= 1 or (len(unique_labels) == 2 and -1 in unique_labels):
        return -1
    s_scores = []
    for i in range(len(X)):
        if labels[i] == -1:
            continue
        same = X[labels == labels[i]]
        a_i = np.mean([euclidean_distance(X[i], p) for p in same if not np.array_equal(X[i], p)]) if len(same) > 1 else 0
        b_i = min(
            np.mean([euclidean_distance(X[i], p) for p in X[labels == cl]])
            for cl in unique_labels if cl != labels[i] and cl != -1
        )
        s_scores.append((b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0)
    return np.mean(s_scores) if s_scores else -1
```

#### Option B: Using Built-In (`DBSCAN` + `silhouette_score`)
```python
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

best_score, best_params, best_labels = -1, {}, None
for eps in [2, 2.5, 3, 3.5, 4]:
    for minpts in range(4, 11):
        labels = DBSCAN(eps=eps, min_samples=minpts).fit_predict(X)
        mask = labels != -1
        if len(set(labels[mask])) >= 2:
            score = silhouette_score(X[mask], labels[mask])
            if score > best_score:
                best_score, best_params, best_labels = score, {'eps': eps, 'minpts': minpts}, labels
```

### Stage 3: K-Distance Graph for Optimal $\varepsilon$ (Custom vs Built-In)

#### Option A: From Scratch (Manual $k$-th Distance + Perpendicular Elbow)
```python
def k_distance_graph(X, k):
    distances = []
    for i in range(len(X)):
        dists = sorted([euclidean_distance(X[i], X[j]) for j in range(len(X)) if i != j])
        distances.append(dists[k - 1])
    distances.sort(reverse=True)

    p1, p2 = np.array([0, distances[0]]), np.array([len(distances) - 1, distances[-1]])
    u = p2 - p1
    u_norm = np.linalg.norm(u)
    max_dist, optimal_eps = 0, distances[0]
    for i, d in enumerate(distances):
        v = np.array([i, d]) - p1
        dist_to_line = abs(u[0] * v[1] - u[1] * v[0]) / u_norm
        if dist_to_line > max_dist:
            max_dist, optimal_eps = dist_to_line, d
    plt.plot(distances)
    plt.axhline(y=optimal_eps, color='r', linestyle='--')
    plt.show()
    return optimal_eps
```

#### Option B: Using Built-In (`sklearn.neighbors.NearestNeighbors`)
```python
from sklearn.neighbors import NearestNeighbors

k = best_params['minpts']
nbrs = NearestNeighbors(n_neighbors=k + 1).fit(X)
distances, _ = nbrs.kneighbors(X)
k_dists = np.sort(distances[:, k])[::-1]     # k-th neighbor distance, descending
plt.plot(k_dists)
plt.title(f"K-Distance Graph (k={k})")
plt.show()
```

### Stage 4: Hierarchical Clustering & Dendrograms (Custom vs Built-In)

#### Option A: From Scratch (`hierarchical_clustering_scratch`)
```python
def hierarchical_clustering_scratch(X, linkage_type='single'):
    n = len(X)
    Z = np.zeros((n - 1, 4))
    clusters = {i: [i] for i in range(n)}
    centroids = {i: X[i] for i in range(n)}
    dist_matrix = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(i + 1, n):
            dist_matrix[i, j] = dist_matrix[j, i] = euclidean_distance(X[i], X[j])

    next_id, active = n, list(range(n))
    for step in range(n - 1):
        min_dist, c1, c2 = np.inf, -1, -1
        for i in range(len(active)):
            for j in range(i + 1, len(active)):
                a, b = active[i], active[j]
                if dist_matrix[a, b] < min_dist:
                    min_dist, c1, c2 = dist_matrix[a, b], a, b

        clusters[next_id] = clusters[c1] + clusters[c2]
        s1, s2 = len(clusters[c1]), len(clusters[c2])
        centroids[next_id] = (s1 * centroids[c1] + s2 * centroids[c2]) / (s1 + s2)
        Z[step] = [c1, c2, min_dist, s1 + s2]
        active.remove(c1); active.remove(c2)

        new_mat = np.full((dist_matrix.shape[0] + 1, dist_matrix.shape[1] + 1), np.inf)
        new_mat[:-1, :-1] = dist_matrix
        dist_matrix = new_mat
        for ac in active:
            if linkage_type == 'single':
                d = min(dist_matrix[c1, ac], dist_matrix[c2, ac])
            elif linkage_type == 'complete':
                d = max(dist_matrix[c1, ac], dist_matrix[c2, ac])
            elif linkage_type == 'centroid':
                d = euclidean_distance(centroids[next_id], centroids[ac])
            dist_matrix[next_id, ac] = dist_matrix[ac, next_id] = d
        active.append(next_id); next_id += 1
    return Z
```

#### Option B: Using Built-In (`scipy.cluster.hierarchy.linkage` + `AgglomerativeClustering`)
```python
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.cluster import AgglomerativeClustering

fig, axes = plt.subplots(3, 1, figsize=(12, 15))
for ax, method in zip(axes, ['single', 'complete', 'centroid']):
    Z = linkage(X, method=method)            # Replaces hierarchical_clustering_scratch
    dendrogram(Z, ax=ax, truncate_mode='lastp', p=30)
    ax.set_title(f"Dendrogram - {method.capitalize()} Linkage")
plt.tight_layout()
plt.show()

# To get flat cluster labels directly (e.g., 5 clusters):
labels = AgglomerativeClustering(n_clusters=5, linkage='complete').fit_predict(X)
```

---

## LAB 11 (EA3): DBSCAN on Air Quality with Standardization & Silhouette Score

**Files Read:** `LAB11/2401179_Q1.py`, `LAB11/run_lab10_experiments.py`, `LAB11/EA3_CS32.pdf`  
**Note:** LAB11 uses built-in `sklearn` directly (`StandardScaler`, `DBSCAN`, `silhouette_score`). If asked to write without `sklearn`, replace `StandardScaler` with `(X - mean) / std` (Stage 0.2), `DBSCAN` with `dbscan_scratch` (LAB10), and `silhouette_score` with `silhouette_score_scratch` (LAB10).

### Stage 1: Imports, Data Cleaning & Z-Score Standardization
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

FEATURES = ["PM2.5", "PM10", "NO2", "SO2"]
df = pd.read_csv("synthetic_urban_air_quality.csv")
data = df[FEATURES].apply(pd.to_numeric, errors="coerce").dropna().reset_index(drop=True)

# Built-in Z-score standardization (or custom: (data - data.mean()) / data.std(ddof=0))
X_scaled = StandardScaler().fit_transform(data)
```

### Stage 2: DBSCAN Across 5 Parameter Settings & Valid Silhouette Check
```python
PARAMETERS = [
    {"eps": 0.5, "min_samples": 3},
    {"eps": 1.2, "min_samples": 3},
    {"eps": 2.1, "min_samples": 3},
    {"eps": 0.8, "min_samples": 5},
    {"eps": 0.8, "min_samples": 7},
]

all_labels = []
for params in PARAMETERS:
    # Built-in: DBSCAN(...).fit_predict(X_scaled)  |  Custom: dbscan_scratch(X_scaled, eps, min_samples)
    labels = DBSCAN(eps=params["eps"], min_samples=params["min_samples"]).fit_predict(X_scaled)
    all_labels.append(labels)

    n_clusters = len(set(labels) - {-1})
    n_noise = int(np.sum(labels == -1))
    noise_pct = (n_noise / len(labels)) * 100.0

    # Filter out noise (-1) and verify 2 <= K <= N_valid - 1
    valid_mask = labels != -1
    valid_labels = labels[valid_mask]
    silhouette = np.nan
    if valid_mask.sum() >= 3:
        unique_clusters, counts = np.unique(valid_labels, return_counts=True)
        if 2 <= len(unique_clusters) < valid_mask.sum() and np.all(counts > 1):
            silhouette = silhouette_score(X_scaled[valid_mask], valid_labels)
```

### Stage 3: Scatter Plot (`PM2.5` vs `PM10`) & Key Observations
```python
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
axes = axes.flatten()
for i, (labels, params) in enumerate(zip(all_labels, PARAMETERS)):
    ax = axes[i]
    for label in sorted(set(labels)):
        mask = labels == label
        if label == -1:
            ax.scatter(data.loc[mask, "PM2.5"], data.loc[mask, "PM10"], c="black", marker="x", s=60, label="Noise")
        else:
            ax.scatter(data.loc[mask, "PM2.5"], data.loc[mask, "PM10"], s=55, alpha=0.8, label=f"Cluster {label}")
    ax.set_title(f"eps={params['eps']}, minPts={params['min_samples']}")
    ax.legend()
axes[-1].axis("off")
plt.tight_layout()
plt.show()
```
* **Key Exam Observations (LAB11):**
  1. **Why standardize?** `PM10` ($>150$) would completely overpower `SO2` ($<25$) in Euclidean distance.
  2. **Effect of `eps` & `minPts`:** Small `eps` (`0.5`) $\to$ high noise (34%); large `eps` (`1.2`, `2.1`) $\to$ collapses into 1 cluster (0% noise). Increasing `minPts` (`5` $\to$ `7` at `eps=0.8`) raises noise (12% $\to$ 22%).
  3. **Silhouette Score around Noise:** Cannot be computed on noise (`-1`) because noise points are dispersed outliers, not a cohesive cluster; also undefined when $K < 2$.

---

## LAB 12 (PA8): Standard vs Weighted K-NN & Continuous-Attribute ID3 Decision Tree

**Files Read:** `LAB12/run_lab11_experiments.py`, `LAB12/PA8_CS32.pdf`

### Problem 1: Standard K-NN vs Weighted K-NN on `heart.csv`

#### Stage 1: Load Data
```python
df = pd.read_csv("heart.csv")
X_raw = df.drop("target", axis=1).values.astype(float)
y = df["target"].values.astype(int)
```

#### Stage 2: Standard K-NN & Weighted K-NN (Custom vs Built-In)

##### Option A: From Scratch (`KNNClassifier`)
```python
class KNNClassifier:
    def __init__(self, k=3, weighted=False, epsilon=0.01):
        self.k, self.weighted, self.epsilon = k, weighted, epsilon

    def fit(self, X, y):
        self.X_train, self.y_train = X, y

    def predict(self, X_test):
        predictions = []
        for x in X_test:
            dists = np.linalg.norm(self.X_train - x, axis=1)
            idx = np.argsort(dists)[:self.k]
            nbr_labels, nbr_dists = self.y_train[idx], dists[idx]

            if not self.weighted:
                unique, counts = np.unique(nbr_labels, return_counts=True)
                pred = unique[np.argmax(counts)]          # Majority vote
            else:
                weights = 1.0 / (nbr_dists + self.epsilon)
                scores = {c: 0.0 for c in np.unique(self.y_train)}
                for lbl, w in zip(nbr_labels, weights):
                    scores[lbl] += w
                pred = max(scores, key=scores.get)        # Weighted vote
            predictions.append(pred)
        return np.array(predictions)
```

##### Option B: Using Built-In (`KNeighborsClassifier`)
```python
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

kf = KFold(n_splits=5, shuffle=True, random_state=42)
for weight_mode in ['uniform', 'distance']:   # 'uniform' = Standard, 'distance' = Weighted
    for k in [3, 5, 7]:
        accs = []
        for train_idx, test_idx in kf.split(X_raw):
            scaler = StandardScaler()
            X_tr = scaler.fit_transform(X_raw[train_idx])
            X_te = scaler.transform(X_raw[test_idx])

            knn = KNeighborsClassifier(n_neighbors=k, weights=weight_mode)
            knn.fit(X_tr, y[train_idx])
            accs.append(accuracy_score(y[test_idx], knn.predict(X_te)))
        print(f"K-NN (weights={weight_mode}, K={k}) Mean Acc: {np.mean(accs):.4f}")
```
* **Formula & Observation:** Weighted K-NN uses $w_i = \frac{1}{d_i + \epsilon}$ ($\epsilon=0.01$), giving closer neighbors stronger votes and outperforming Standard K-NN across $K \in \{3, 5, 7\}$.

---

### Problem 2: Continuous-Attribute ID3 Decision Tree (`diabetes_prediction_dataset.csv`)

#### Stage 1: Load & Encode Data
```python
df = pd.read_csv("diabetes_prediction_dataset.csv")
df_encoded = pd.get_dummies(df, columns=["gender", "smoking_history"], drop_first=True)
df_sample = df_encoded.sample(n=5000, random_state=42).reset_index(drop=True)
X = df_sample.drop("diabetes", axis=1).values.astype(float)
y = df_sample["diabetes"].values.astype(int)
```

#### Stage 2: ID3 Decision Tree (Custom vs Built-In)

##### Option A: From Scratch (`entropy`, `information_gain`, `ID3DecisionTree`)
```python
def entropy(y):
    if len(y) == 0:
        return 0.0
    _, counts = np.unique(y, return_counts=True)
    probs = counts / len(y)
    return -np.sum(probs * np.log2(probs + 1e-15))

def information_gain(X_col, y, threshold):
    left = X_col <= threshold
    if np.sum(left) == 0 or np.sum(~left) == 0:
        return 0.0
    n = len(y)
    return entropy(y) - ((np.sum(left) / n) * entropy(y[left]) + (np.sum(~left) / n) * entropy(y[~left]))

class DecisionTreeNode:
    def __init__(self, feature=None, threshold=None, left=None, right=None, value=None):
        self.feature, self.threshold, self.left, self.right, self.value = feature, threshold, left, right, value
    @property
    def is_leaf(self):
        return self.value is not None

class ID3DecisionTree:
    def __init__(self, max_depth=6, min_samples_split=15):
        self.max_depth, self.min_samples_split, self.root = max_depth, min_samples_split, None

    def fit(self, X, y):
        self.root = self._grow_tree(X, y, 0)

    def _grow_tree(self, X, y, depth):
        n_samples, n_features = X.shape
        if len(np.unique(y)) == 1 or depth >= self.max_depth or n_samples < self.min_samples_split:
            u, c = np.unique(y, return_counts=True)
            return DecisionTreeNode(value=u[np.argmax(c)])

        best_gain, best_feat, best_thresh = -1.0, None, None
        for feat_idx in range(n_features):
            col = X[:, feat_idx]
            for thresh in np.percentile(col, np.linspace(10, 90, 9)):
                gain = information_gain(col, y, thresh)
                if gain > best_gain:
                    best_gain, best_feat, best_thresh = gain, feat_idx, thresh

        if best_gain <= 1e-5:
            u, c = np.unique(y, return_counts=True)
            return DecisionTreeNode(value=u[np.argmax(c)])

        left = X[:, best_feat] <= best_thresh
        return DecisionTreeNode(
            feature=best_feat, threshold=best_thresh,
            left=self._grow_tree(X[left], y[left], depth + 1),
            right=self._grow_tree(X[~left], y[~left], depth + 1)
        )

    def _traverse(self, x, node):
        if node.is_leaf:
            return node.value
        return self._traverse(x, node.left if x[node.feature] <= node.threshold else node.right)

    def predict(self, X):
        return np.array([self._traverse(x, self.root) for x in X])
```

##### Option B: Using Built-In (`DecisionTreeClassifier(criterion='entropy')`)
```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)
for fold, (train_idx, test_idx) in enumerate(kf.split(X), start=1):
    # criterion='entropy' uses Information Gain (ID3/C4.5 style)
    dt = DecisionTreeClassifier(criterion='entropy', max_depth=6, min_samples_split=15, random_state=42)
    dt.fit(X[train_idx], y[train_idx])
    y_pred = dt.predict(X[test_idx])
    print(f"Fold {fold} Acc: {accuracy_score(y[test_idx], y_pred):.4f}")
```
* **Note:** Feature scaling is **NOT** needed for Decision Trees.

---

## LAB 13 (PA9): Perceptron (OR/NAND), Categorical Naive Bayes & Gaussian Naive Bayes

**Files Read:** `LAB13/answer1.py`, `LAB13/PA9_CS32.pdf`

### Question 1: Perceptron (OR & NAND Gates, Step Function, 2 Epochs, 80:20 Split)

#### Option A: From Scratch (Pure Python)
```python
import random

def step_function(z):
    return 1 if z >= 0 else 0

def run_perceptron(raw_data, epochs=2, lr=0.1, seed=42):
    random.seed(seed)
    data = raw_data * 5                  # Replicate 4 rows -> 20 samples (16 train : 4 test)
    random.shuffle(data)
    split_idx = int(0.8 * len(data))
    train_data, test_data = data[:split_idx], data[split_idx:]

    w = [random.uniform(-0.5, 0.5) for _ in range(len(raw_data[0][0]))]
    b = random.uniform(-0.5, 0.5)

    for epoch in range(epochs):
        for x, y in train_data:
            z = sum(wi * xi for wi, xi in zip(w, x)) + b
            err = y - step_function(z)
            w = [wi + lr * err * xi for wi, xi in zip(w, x)]
            b = b + lr * err

    train_pred = [step_function(sum(wi * xi for wi, xi in zip(w, x)) + b) for x, _ in train_data]
    test_pred  = [step_function(sum(wi * xi for wi, xi in zip(w, x)) + b) for x, _ in test_data]
    return train_pred, test_pred

or_gate   = [([0, 0], 0), ([0, 1], 1), ([1, 0], 1), ([1, 1], 1)]
nand_gate = [([0, 0], 1), ([0, 1], 1), ([1, 0], 1), ([1, 1], 0)]
```

#### Option B: Using Built-In (`sklearn.linear_model.Perceptron`)
```python
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

data = or_gate * 5
X = np.array([x for x, _ in data])
y = np.array([lbl for _, lbl in data])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = Perceptron(max_iter=2, eta0=0.1, tol=None, random_state=42)
clf.fit(X_train, y_train)
print(classification_report(y_test, clf.predict(X_test), zero_division=0))
```

---

### Question 2: Categorical Naive Bayes (E-Commerce Purchase Prediction)

#### Dataset
```python
dataset_q2 = [
    ("Young", "High", "long", "No", "No"),   ("Young", "High", "long", "Yes", "No"),
    ("Middle", "High", "long", "No", "Yes"), ("Senior", "Medium", "long", "No", "Yes"),
    ("Senior", "Low", "short", "No", "Yes"), ("Senior", "Low", "short", "Yes", "No"),
    ("Middle", "Low", "short", "Yes", "Yes"),("Young", "Medium", "long", "No", "No"),
    ("Young", "Low", "short", "No", "Yes"),  ("Senior", "Medium", "short", "No", "Yes"),
    ("Young", "Medium", "short", "Yes", "Yes"),("Middle", "Medium", "long", "Yes", "Yes"),
    ("Middle", "High", "short", "No", "Yes"),("Senior", "Medium", "long", "Yes", "No"),
]
X_q2 = [row[:-1] for row in dataset_q2]
y_q2 = [row[-1] for row in dataset_q2]
```

#### Option A: From Scratch (Pure Python with Laplace Smoothing)
```python
class CategoricalNaiveBayes:
    def __init__(self, laplace=1.0):
        self.laplace = laplace

    def fit(self, X, y):
        self.classes = sorted(list(set(y)))
        n_samples, n_features = len(y), len(X[0])
        self.vocab = {i: set(row[i] for row in X) for i in range(n_features)}
        self.priors = {}
        self.likelihoods = {c: {i: {} for i in range(n_features)} for c in self.classes}

        for c in self.classes:
            c_idx = [idx for idx, t in enumerate(y) if t == c]
            self.priors[c] = len(c_idx) / n_samples
            for i in range(n_features):
                vals = [X[idx][i] for idx in c_idx]
                for v in self.vocab[i]:
                    self.likelihoods[c][i][v] = (vals.count(v) + self.laplace) / (len(c_idx) + self.laplace * len(self.vocab[i]))

    def predict_proba(self, x):
        posteriors = {}
        for c in self.classes:
            p = self.priors[c]
            for i, val in enumerate(x):
                p *= self.likelihoods[c][i].get(val, 1.0 / (len(self.vocab[i]) + 1))
            posteriors[c] = p
        total = sum(posteriors.values())
        return {c: posteriors[c] / total for c in self.classes}

    def predict(self, X):
        return [max(self.predict_proba(x), key=self.predict_proba(x).get) for x in X]

# Predict for ("Middle", "High", "long", "Yes") -> 'Yes'
```

#### Option B: Using Built-In (`OrdinalEncoder` + `CategoricalNB`)
```python
from sklearn.preprocessing import OrdinalEncoder
from sklearn.naive_bayes import CategoricalNB

encoder = OrdinalEncoder()
X_enc = encoder.fit_transform(X_q2)          # Converts strings to integers 0, 1, 2...

cnb = CategoricalNB(alpha=1.0)               # alpha=1.0 -> Laplace smoothing
cnb.fit(X_enc, y_q2)

test_enc = encoder.transform([["Middle", "High", "long", "Yes"]])
print("Prediction:", cnb.predict(test_enc), "Probs:", cnb.predict_proba(test_enc))
```

---

### Question 3: Gaussian Naive Bayes (Continuous Diabetes Dataset)

#### Option A: From Scratch (Pure Python with Log-Sum-Exp)
```python
import math

class GaussianNaiveBayes:
    def _mean(self, nums): return sum(nums) / len(nums)
    def _stdev(self, nums):
        avg = self._mean(nums)
        return math.sqrt(sum((x - avg) ** 2 for x in nums) / (len(nums) - 1))

    def _gaussian_density(self, x, m, s):
        if s == 0: return 1.0 if x == m else 0.0
        return (1 / (math.sqrt(2 * math.pi) * s)) * math.exp(-((x - m) ** 2) / (2 * (s ** 2)))

    def fit(self, dataset):
        self.classes = sorted(list(set(row[-1] for row in dataset)))
        sep = {c: [row[:-1] for row in dataset if row[-1] == c] for c in self.classes}
        self.priors = {c: len(sep[c]) / len(dataset) for c in self.classes}
        self.stats = {c: [(self._mean(col), self._stdev(col)) for col in zip(*sep[c])] for c in self.classes}

    def predict_proba(self, x):
        posteriors = {}
        for c in self.classes:
            log_p = math.log(self.priors[c])
            for i, (m, s) in enumerate(self.stats[c]):
                log_p += math.log(max(self._gaussian_density(x[i], m, s), 1e-12))
            posteriors[c] = log_p
        max_log = max(posteriors.values())
        exp_p = {c: math.exp(v - max_log) for c, v in posteriors.items()}
        total = sum(exp_p.values())
        return {c: exp_p[c] / total for c in self.classes}

    def predict(self, X):
        return [max(self.predict_proba(x), key=self.predict_proba(x).get) for x in X]
```

#### Option B: Using Built-In (`sklearn.naive_bayes.GaussianNB`)
```python
from sklearn.naive_bayes import GaussianNB

X_q3 = np.array([row[:-1] for row in synthetic_data])
y_q3 = np.array([row[-1] for row in synthetic_data])

gnb = GaussianNB()
gnb.fit(X_q3, y_q3)
print("Prediction:", gnb.predict([[142, 29, 42]]), "Probs:", gnb.predict_proba([[142, 29, 42]]))
```

---

## Master Built-In Imports & Final Exam Cheat Sheet

### 1. From-Scratch vs Built-In Comparison Table (LAB7 to LAB13)

| Lab | Task / Algorithm | From-Scratch Implementation | Built-In `sklearn` / `scipy` Equivalent | Scaling Needed? |
| :--- | :--- | :--- | :--- | :--- |
| **LAB7** | Binary Logistic Regression | `CustomLogisticRegression` (Batch GD) | `LogisticRegression(max_iter=100)` + `.predict_proba()` | **Yes** (Z-score) |
| **LAB8 P1** | Multi-Class Logistic (OvA) | `train_one_vs_all` + `batch_gradient_descent` | `OneVsRestClassifier(LogisticRegression())` | **Yes** (Z-score) |
| **LAB8 P2** | K-Means + PCA (2D Plot) | `k_means()` + `get_first_two_pcs()` | `KMeans(n_clusters=K)` + `PCA(n_components=2)` | **Yes** (Z-score) |
| **LAB9** | SGD Logistic Regression | `sgd_logistic_regression()` (per-sample update) | `SGDClassifier(loss='log_loss', learning_rate='constant', eta0=0.01)` | **Compare No vs Yes** |
| **LAB10** | DBSCAN + K-Dist + Hierarchical | `dbscan_scratch()`, `k_distance_graph()`, `hierarchical_clustering_scratch()` | `DBSCAN()`, `NearestNeighbors()`, `scipy.cluster.hierarchy.linkage()` | Distance-based |
| **LAB11** | Urban Air Quality DBSCAN | `dbscan_scratch()` + `silhouette_score_scratch()` | `StandardScaler()`, `DBSCAN()`, `silhouette_score()` | **Yes** (`StandardScaler`) |
| **LAB12 P1** | Standard & Weighted K-NN | `KNNClassifier(weighted=False/True)` | `KNeighborsClassifier(n_neighbors=k, weights='uniform'/'distance')` | **Yes** (Z-score) |
| **LAB12 P2** | Continuous ID3 Tree | `ID3DecisionTree` (Entropy + Percentiles) | `DecisionTreeClassifier(criterion='entropy', max_depth=6)` | **No** |
| **LAB13 Q1** | Perceptron (OR / NAND) | `step_function` + weight update loop | `Perceptron(max_iter=2, eta0=0.1, tol=None)` | No (Binary 0/1) |
| **LAB13 Q2** | Categorical Naive Bayes | `CategoricalNaiveBayes(laplace=1.0)` | `OrdinalEncoder()` + `CategoricalNB(alpha=1.0)` | No |
| **LAB13 Q3** | Gaussian Naive Bayes | `GaussianNaiveBayes` (PDF + log-sum-exp) | `GaussianNB()` | No |

### 2. Core Mathematical Formulas to Memorize
* **Z-Score Standardization:** $z = \frac{x - \mu}{\sigma}$
* **Sigmoid & Binary Cross-Entropy:** $\sigma(z) = \frac{1}{1 + e^{-z}}$, $\quad J(w) = -\frac{1}{m}\sum [y\log\hat{y} + (1-y)\log(1-\hat{y})]$
* **Batch GD vs SGD Update:** Batch: $w \leftarrow w - \frac{\alpha}{m} X^T(\hat{y}-y)$ $\quad\vert\quad$ SGD: $\theta \leftarrow \theta - \alpha (h_i - y_i) x_i$
* **Weighted K-NN:** $w_i = \frac{1}{d_i + \epsilon}$
* **Entropy & Information Gain:** $H(S) = -\sum p_c \log_2 p_c$, $\quad IG = H(S) - \sum \frac{|S_v|}{|S|} H(S_v)$
* **Perceptron Update:** $w \leftarrow w + \eta (y - \hat{y}) x$, $\quad b \leftarrow b + \eta (y - \hat{y})$
* **Laplace Naive Bayes & Gaussian PDF:** $P(v\mid C) = \frac{\text{count}(v,C)+\alpha}{N_C + \alpha |V|}$, $\quad P(x\mid C) = \frac{1}{\sqrt{2\pi}\sigma} e^{-\frac{(x-\mu)^2}{2\sigma^2}}$
* **Metrics:**
  $$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}, \quad \text{Precision} = \frac{TP}{TP + FP}, \quad \text{Recall} = \frac{TP}{TP + FN}, \quad s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

Good luck on your ML lab exam today!

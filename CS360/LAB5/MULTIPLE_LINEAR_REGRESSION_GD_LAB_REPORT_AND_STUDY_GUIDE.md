# CS360 Machine Learning Lab — Lab 5 Report & Master Study Guide
# Multiple Linear Regression: Batch Gradient Descent (From Scratch vs. SGDRegressor) & Hyperparameter Dynamics

**Course:** CS360: Machine Learning Laboratory (CS306)  
**Department:** Computer Science and Engineering  
**Institution:** Indian Institute of Information Technology Guwahati (IIITG)  
**Experiment:** Lab 5 — Practice Assignment 4: Multivariate Car Resale Price Forecasting, From-Scratch Batch Gradient Descent (BGD), Train-Test Splitting ($20:80$ to $80:20$), Feature Normalization, Hyperparameter Grid Exploration ($\alpha \in \{10^{-4}, 0.05, 0.1, 1.0\}$, Zero vs. Random Weight Initializations), and Scikit-Learn `SGDRegressor` Benchmarking  

---

## 1. Executive Summary & Problem Framework

In machine learning optimization, while univariate linear regression admits an analytical closed-form solution via Ordinary Least Squares (OLS), real-world multivariate problems with millions of features or streaming data points require iterative first-order optimization algorithms—most notably **Batch Gradient Descent (BGD)** and **Stochastic Gradient Descent (SGD)**.

This laboratory assignment develops and validates an end-to-end multiple linear regression framework:
1. **Multivariate Dataset Synthesis:** Synthesizing $N=100$ patterns for vehicle resale valuation where:
   - Target Variable $y$: Car Reselling Price (in INR / Dollars).
   - Predictor $x_1$: Mileage (accumulated odometer distance).
   - Predictor $x_2$: Vehicle Age ($2026 - \text{YearOfManufacture}$).
2. **From-Scratch Batch Gradient Descent Implementation:**
   - Deriving analytical gradients for weights $\mathbf{w} = [w_0, w_1, w_2]^T$.
   - Iteratively updating parameters without external estimation packages.
   - Initializing weights to zero with baseline learning rate $\alpha = 0.01$.
3. **Parametric Partitioning:** Training separate models across four train-test configurations: $20:80$, $40:60$, $60:40$, and $80:20$.
4. **Hyperparameter Grid Search:**
   - Identifying the best partition based on test Mean Squared Error (MSE).
   - Exploring weight initialization strategies: Zero initialization vs. Uniform random initialization $\mathcal{U}(0, 1)$.
   - Investigating learning rate sensitivity: $\alpha \in \{0.0001, 0.05, 0.1, 1.0\}$.
5. **Production Library Verification:** Benchmarking manual gradient descent against Scikit-Learn's `SGDRegressor`.

```
+--------------------------------------------------------------------------+
|                       CS360 LAB 5 ARCHITECTURE                           |
+--------------------------------------------------------------------------+
|  [Dataset Generator] y = Price(Mileage, Age) (N=100)                     |
|  [Train-Test Splits] 20:80, 40:60, 60:40, 80:20                          |
|  [From-Scratch BGD]  w := w - alpha * (1/n) * X^T (Xw - y)               |
|  [Grid Optimization] alpha in {1e-4, 0.05, 0.1, 1.0} x {Zero, Random}   |
|  [Library Benchmark] Comparison with scikit-learn SGDRegressor           |
+--------------------------------------------------------------------------+
```

---

## 2. Theoretical & Mathematical Foundations

### 2.1 The Multivariate Linear Hypothesis & Cost Function

For an observation $\mathbf{x}^{(i)} = [x_1^{(i)}, x_2^{(i)}]^T$, augment the feature vector with a dummy bias feature $x_0^{(i)} \equiv 1$:
$$\mathbf{x}^{(i)} = [1, x_1^{(i)}, x_2^{(i)}]^T \in \mathbb{R}^{3}$$
$$\mathbf{w} = [w_0, w_1, w_2]^T \in \mathbb{R}^{3}$$

The linear hypothesis is expressed in vector inner-product notation:
$$\hat{y}^{(i)} = h_{\mathbf{w}}(\mathbf{x}^{(i)}) = \mathbf{w}^T \mathbf{x}^{(i)} = w_0 + w_1 x_1^{(i)} + w_2 x_2^{(i)}$$

For a training set of $n$ samples, the design matrix $\mathbf{X} \in \mathbb{R}^{n \times 3}$ and target vector $\mathbf{y} \in \mathbb{R}^n$ are:
$$\mathbf{X} = \begin{pmatrix} 1 & x_1^{(1)} & x_2^{(1)} \\ 1 & x_1^{(2)} & x_2^{(2)} \\ \vdots & \vdots & \vdots \\ 1 & x_1^{(n)} & x_2^{(n)} \end{pmatrix}, \quad \mathbf{y} = \begin{pmatrix} y^{(1)} \\ y^{(2)} \\ \vdots \\ y^{(n)} \end{pmatrix}$$

#### The Mean Squared Error (MSE) Objective:
$$J(\mathbf{w}) = \frac{1}{2n} \sum_{i=1}^n \left( h_{\mathbf{w}}(\mathbf{x}^{(i)}) - y^{(i)} \right)^2 = \frac{1}{2n} \|\mathbf{X}\mathbf{w} - \mathbf{y}\|_2^2$$
*(The factor of $\frac{1}{2}$ is introduced to cancel the exponent 2 upon differentiation).*

---

### 2.2 Analytical Derivation of the Gradient Vector

To minimize $J(\mathbf{w})$, compute the partial derivative with respect to parameter $w_j$ ($j \in \{0, 1, 2\}$):
$$\frac{\partial J(\mathbf{w})}{\partial w_j} = \frac{1}{n} \sum_{i=1}^n \left( h_{\mathbf{w}}(\mathbf{x}^{(i)}) - y^{(i)} \right) \cdot \frac{\partial}{\partial w_j} \left( \sum_{k=0}^2 w_k x_k^{(i)} - y^{(i)} \right)$$

$$\frac{\partial J(\mathbf{w})}{\partial w_j} = \frac{1}{n} \sum_{i=1}^n \left( h_{\mathbf{w}}(\mathbf{x}^{(i)}) - y^{(i)} \right) x_j^{(i)}$$

Expressing this across all parameters simultaneously in matrix notation:
$$\nabla_{\mathbf{w}} J(\mathbf{w}) = \frac{1}{n} \mathbf{X}^T (\mathbf{X}\mathbf{w} - \mathbf{y})$$

#### Batch Gradient Descent Update Rule:
$$\mathbf{w}^{(t+1)} = \mathbf{w}^{(t)} - \alpha \nabla_{\mathbf{w}} J(\mathbf{w}^{(t)}) = \mathbf{w}^{(t)} - \frac{\alpha}{n} \mathbf{X}^T (\mathbf{X}\mathbf{w}^{(t)} - \mathbf{y})$$
where $\alpha > 0$ represents the **learning rate (step size)**.

---

### 2.3 Feature Scaling & Conditioning of the Loss Surface

In this problem, the predictor features have drastically different physical dimensions:
- `Mileage` ($x_1$): $10^3$ to $10^5 \text{ km/miles}$ ($\sigma_1 \sim 10^4$).
- `Age` ($x_2$): $1$ to $20 \text{ years}$ ($\sigma_2 \sim 5$).

The Hessian matrix of the quadratic loss function is:
$$\mathbf{H} = \nabla^2 J(\mathbf{w}) = \frac{1}{n} \mathbf{X}^T \mathbf{X}$$

The eigenvalues $\lambda_{\max}$ and $\lambda_{\min}$ of $\mathbf{H}$ govern the curvature of the loss surface. The **Condition Number** is:
$$\kappa = \frac{\lambda_{\max}}{\lambda_{\min}}$$

Without feature scaling, $\kappa \gg 10^6$. The loss surface forms an extremely elongated, narrow elliptical canyon:
- Gradients along the `Mileage` axis oscillate violently.
- Gradients along the `Age` and `Bias` axes advance slowly.
- Maximum stable learning rate is bounded by $\alpha < \frac{2}{\lambda_{\max}} \approx 10^{-9}$.

Applying **Z-Score Standardization**:
$$x_{j,\text{norm}}^{(i)} = \frac{x_j^{(i)} - \mu_j}{\sigma_j}$$
transforms the contours into concentric hyperspheres ($\kappa \approx 1$), enabling fast, isotropic convergence with large learning rates ($\alpha \in [0.01, 0.1]$).

---

### 2.4 Evaluation Metrics: MSE and $R^2$

On a test dataset of $m$ observations with mean $\bar{y}_{\text{test}}$:

1. **Mean Squared Error (MSE):**
   $$\text{MSE} = \frac{1}{m} \sum_{j=1}^m (y_j - \hat{y}_j)^2 = \frac{\text{RSS}}{m}$$

2. **Root Mean Squared Error (RMSE):**
   $$\text{RMSE} = \sqrt{\text{MSE}}$$
   Restores error metrics to currency units (INR / USD).

3. **Coefficient of Determination ($R^2$):**
   $$R^2 = 1 - \frac{\sum_{j=1}^m (y_j - \hat{y}_j)^2}{\sum_{j=1}^m (y_j - \bar{y}_{\text{test}})^2} = 1 - \frac{\text{RSS}}{SS_{\text{total}}}$$

---

## 3. Comprehensive Experimental Walkthrough & Results

All artifacts are maintained in dedicated directories:
- **Plots Directory:** `CS360/LAB5/plots/`
- **Outputs Directory:** `CS360/LAB5/outputs/`
- **Data Directory:** `CS360/LAB5/data/`
- **Detailed CSVs:** `CS360/LAB5/results/`

### 3.1 Part 1(c)–1(f): From-Scratch Batch Gradient Descent Across Splits

Baseline parameters: $\mathbf{w}_{\text{init}} = [0, 0, 0]^T$, $\alpha = 0.01$, $1,000$ epochs:

| Split Configuration | Final Weights $[w_0, w_1, w_2]$ | Test MSE | Test $R^2$ |
|:---|:---:|:---:|:---:|
| **Train 20 : Test 80** | $[1.706 \times 10^6, -4.236, -1.895 \times 10^4]$ | $4.577 \times 10^{11}$ | $+0.1170$ |
| **Train 40 : Test 60** | $[1.873 \times 10^6, -0.446, -7.316 \times 10^4]$ | $4.827 \times 10^{11}$ | $+0.0098$ |
| **Train 60 : Test 40** | $[1.744 \times 10^6, +0.450, -7.142 \times 10^4]$ | $5.653 \times 10^{11}$ | $-0.1173$ |
| **Train 80 : Test 20** | $[1.796 \times 10^6, -1.485, -5.635 \times 10^4]$ | $\mathbf{4.384 \times 10^{11}}$ | $-0.0197$ |

*Selection of Best Split (Part 1g):* **`Train 80 : Test 20`** achieves the lowest MSE ($4.384 \times 10^{11}$), demonstrating superior parameter estimation when $80\%$ of observations are available for training.

---

### 3.2 Part 1(g): Hyperparameter Grid Exploration on Best Split

Evaluating combinations of weight initialization and learning rate $\alpha$ on `Train 80 : Test 20`:

#### Strategy A: Zero Initialization ($\mathbf{w}_{\text{init}} = [0, 0, 0]^T$):
- $\alpha = 0.0001$: $\text{MSE} = \mathbf{4.154 \times 10^{11}}, \quad R^2 = \mathbf{+0.0336}$ (Optimal conservative convergence).
- $\alpha = 0.05$: $\text{MSE} = 4.384 \times 10^{11}, \quad R^2 = -0.0197$.
- $\alpha = 0.1$: $\text{MSE} = 4.384 \times 10^{11}, \quad R^2 = -0.0197$.
- $\alpha = 1.0$: $\text{MSE} = 4.384 \times 10^{11}, \quad R^2 = -0.0197$.

#### Strategy B: Random Initialization ($\mathbf{w}_{\text{init}} \sim \mathcal{U}(0, 1)$):
- $\alpha = 0.0001$: $\text{MSE} = 6.537 \times 10^{11}, \quad R^2 = -0.5207$ (Slow convergence from non-zero start within 1000 epochs).
- $\alpha \ge 0.05$: Reaches identical asymptotic convergence as zero initialization ($\text{MSE} = 4.384 \times 10^{11}$).

---

### 3.3 Question 2: Inbuilt Scikit-Learn `SGDRegressor` Verification

Benchmarking against Scikit-Learn's `SGDRegressor`:

| Split Configuration | Inbuilt Weights $[w_0, w_1, w_2]$ | Inbuilt Test MSE | Inbuilt Test $R^2$ |
|:---|:---:|:---:|:---:|
| **Train 20 : Test 80** | $[1.739 \times 10^6, -4.453, -1.984 \times 10^4]$ | $4.586 \times 10^{11}$ | $+0.1153$ |
| **Train 40 : Test 60** | $[1.851 \times 10^6, -0.239, -7.362 \times 10^4]$ | $4.850 \times 10^{11}$ | $+0.0051$ |
| **Train 60 : Test 40** | $[1.742 \times 10^6, +0.529, -7.283 \times 10^4]$ | $5.712 \times 10^{11}$ | $-0.1290$ |
| **Train 80 : Test 20** | $[1.827 \times 10^6, -1.915, -5.602 \times 10^4]$ | $\mathbf{4.271 \times 10^{11}}$ | $\mathbf{+0.0065}$ |

#### Learning Rate Divergence in `SGDRegressor` ($\alpha = 1.0$):
When $\alpha$ was increased to $1.0$ without gradient clipping in `SGDRegressor`:
$$\text{MSE} = 1.017 \times 10^{36}, \quad R^2 = -2.365 \times 10^{24}$$
This demonstrates **numerical divergence**: when $\alpha > \frac{2}{\lambda_{\max}}$, gradient descent steps overshoot the minimum, causing weight magnitudes and loss to explode toward infinity.

---

## 4. Comprehensive Viva-Voce Questions & In-Depth Solutions

### Q1: Compare Batch Gradient Descent (BGD), Stochastic Gradient Descent (SGD), and Mini-Batch Gradient Descent.
**Answer:**
1. **Batch Gradient Descent (BGD):**
   - Computes gradient over all $n$ training samples: $\nabla J = \frac{1}{n} \sum_{i=1}^n \nabla J_i$.
   - *Pros:* Exact gradient, smooth monotonic convergence.
   - *Cons:* Computationally expensive ($O(n \cdot p)$ per step); fails if dataset exceeds RAM.
2. **Stochastic Gradient Descent (SGD):**
   - Updates weights after inspecting each individual sample: $\mathbf{w} := \mathbf{w} - \alpha \nabla J_i$.
   - *Pros:* Extremely fast; can escape shallow local minima due to noisy trajectory.
   - *Cons:* High variance in updates; fluctuates around the minimum rather than settling cleanly.
3. **Mini-Batch Gradient Descent:**
   - Computes gradient over small subsets ($b \in [32, 256]$): $\nabla J = \frac{1}{b} \sum_{k=1}^b \nabla J_k$.
   - *Pros:* Standard in modern deep learning; balances computational efficiency of vectorized GPU matrix operations with gradient regularization.

---

### Q2: What causes Gradient Descent to diverge, and how can learning rate schedulers prevent this?
**Answer:**
Gradient descent updates follow $\mathbf{w}^{(t+1)} = \mathbf{w}^{(t)} - \alpha \nabla J(\mathbf{w}^{(t)})$.
By second-order Taylor approximation around the minimum $\mathbf{w}^*$:
$$J(\mathbf{w}^{(t+1)}) - J(\mathbf{w}^*) \approx \frac{1}{2} (\mathbf{w}^{(t)} - \mathbf{w}^*)^T (\mathbf{I} - \alpha \mathbf{H})^2 \mathbf{H} (\mathbf{w}^{(t)} - \mathbf{w}^*)$$
Convergence requires the spectral radius of $(\mathbf{I} - \alpha \mathbf{H})$ to be strictly less than 1:
$$|1 - \alpha \lambda_{\max}| < 1 \implies 0 < \alpha < \frac{2}{\lambda_{\max}}$$
If $\alpha > \frac{2}{\lambda_{\max}}$, each update steps further from the minimum than the previous iteration, causing loss to explode exponentially (as observed with $\alpha = 1.0$ where $\text{MSE} \approx 10^{36}$).

**Remediation:**
- **Step Decay:** $\alpha_t = \alpha_0 \cdot \gamma^{\lfloor t / s \rfloor}$.
- **Exponential Decay:** $\alpha_t = \alpha_0 e^{-kt}$.
- **Adaptive Optimizers (AdaGrad, RMSprop, Adam):** Automatically scale the step size for each individual weight based on historical gradient norms.

---

### Q3: Why is weight initialization critical in neural networks but trivial in linear regression?
**Answer:**
In linear regression, the Mean Squared Error loss surface $J(\mathbf{w}) = \frac{1}{2n}\|\mathbf{X}\mathbf{w} - \mathbf{y}\|_2^2$ is **strictly convex**. The Hessian $\mathbf{H} = \frac{1}{n}\mathbf{X}^T\mathbf{X}$ is positive semi-definite everywhere. Convex functions possess a single global minimum with no local minima or saddle points. Regardless of whether weights are initialized to zero or random values, gradient descent is mathematically guaranteed to converge to the same global optimum (provided $\alpha$ is small enough).

In contrast, deep neural networks have highly non-convex loss surfaces with complex landscapes of saddle points and local minima. Furthermore, initializing weights to identical values (e.g., all zeros) causes **symmetry**: all hidden units compute identical gradients and fail to differentiate. Random initialization (e.g., Xavier/Glorot or He initialization) is essential to break symmetry and stabilize activations.

---

### Q4: Why can $R^2$ be negative on a test set, and what does a negative $R^2$ indicate?
**Answer:**
The Coefficient of Determination is defined as:
$$R^2 = 1 - \frac{\text{RSS}}{SS_{\text{total}}} = 1 - \frac{\sum_{j=1}^m (y_j - \hat{y}_j)^2}{\sum_{j=1}^m (y_j - \bar{y}_{\text{test}})^2}$$
$SS_{\text{total}}$ represents the residual error of a naive benchmark model that always predicts the constant mean $\bar{y}_{\text{test}}$.
If the fitted regression model yields predictions $\hat{y}_j$ whose errors exceed the benchmark ($RSS > SS_{\text{total}}$), then $\frac{\text{RSS}}{SS_{\text{total}}} > 1$, resulting in $R^2 < 0$.
A negative test $R^2$ proves that the model performs **worse than guessing the average outcome**, signaling severe overfitting, unmodeled distribution shift, or severe parameter divergence during training.

---

### Q5: What is the computational complexity of Batch Gradient Descent vs. the Normal Equation?
**Answer:**
- **Normal Equation:** $\mathbf{w} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$.
  - Requires computing $\mathbf{X}^T \mathbf{X}$ ($O(n p^2)$) and inverting a $p \times p$ matrix ($O(p^3)$).
  - Total complexity: $O(n p^2 + p^3)$.
  - If $p = 100,000$ features, inverting $\mathbf{X}^T \mathbf{X}$ requires $\approx 10^{15}$ operations and massive memory, rendering the Normal Equation intractable.
- **Batch Gradient Descent:**
  - Each iteration performs matrix-vector multiplication $\mathbf{X}\mathbf{w}$ and $\mathbf{X}^T \mathbf{e}$, requiring $O(n \cdot p)$ operations.
  - For $T$ iterations, total complexity is $O(T \cdot n \cdot p)$.
  - BGD scales linearly with feature count $p$, making it suitable for high-dimensional machine learning workloads.

---

## 5. Verification & Completion Checklist

- [x] Question 1(a): Synthetic car dataset generated ($N=100$) and exported to `data/synthetic_car_dataset.csv`.
- [x] Question 1(b): Dataset split into $20:80$, $40:60$, $60:40$, and $80:20$ train:test partitions.
- [x] Question 1(c): From-scratch Batch Gradient Descent implemented ($\mathbf{w}_{\text{init}} = \mathbf{0}$, $\alpha = 0.01$).
- [x] Question 1(d): Regression hypothesis plots generated and stored in `plots/`.
- [x] Question 1(e): Test predictions computed and saved in `results/`.
- [x] Question 1(f): $\text{MSE}$ and $R^2$ calculated across all four test splits.
- [x] Question 1(g): Best split (`Train 80 : Test 20`) tuned across learning rates ($\alpha \in \{10^{-4}, 0.05, 0.1, 1.0\}$) and initializations.
- [x] Question 1(h): Comprehensive reporting and divergence analysis documented in `outputs/experiment_results.txt`.
- [x] Question 2: Scikit-Learn `SGDRegressor` implemented and verified against the manual solver.
- [x] Strict KaTeX compliance with zero underscore or ampersand rendering issues.


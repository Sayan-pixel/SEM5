# CS360 Machine Learning Lab — Lab 3 Report & Master Study Guide
# Advanced Correlation Analysis: Non-Linearity, Monotonicity & Multivariate Association

**Course:** CS360: Machine Learning Laboratory (CS306)  
**Department:** Computer Science and Engineering  
**Institution:** Indian Institute of Information Technology Guwahati (IIITG)  
**Experiment:** Lab 3 — Practice Assignment 2: High vs. Low Variance Synthesis, Non-Linear Quadratic Association, Monotonic vs. Non-Monotonic Dynamics (Pearson vs. Spearman), and Multivariate Car Resale Price Correlation Matrix  

---

## 1. Executive Summary & Problem Framework

In machine learning and feature selection pipelines, selecting an inappropriate association metric can lead to catastrophic feature pruning or misinformed inductive biases. Standard linear estimators, such as Ordinary Least Squares (OLS) regression, rely on **Pearson correlation** to detect feature relevance. However, real-world data frequently exhibits non-linear manifolds, heteroskedasticity, and non-monotonic trends where Pearson correlation breaks down completely.

This laboratory assignment establishes core empirical and analytical foundations across four distinct tasks:
1. **Problem 1 (High vs. Low Variance):** Comparing the interplay between feature variance, covariance scale-dependence, and standardized correlation across high-noise and low-noise bivariate Gaussian models.
2. **Problem 2 (Non-Linear Quadratic Relationship):** Proving both theoretically and empirically that strong deterministic non-linear dependencies ($Y = X^2$) yield $r \approx 0$, demonstrating that zero Pearson correlation does not imply statistical independence.
3. **Problem 3 (Monotonic vs. Non-Monotonic Dynamics):** Evaluating the comparative performance of **Pearson's Product-Moment Correlation** ($r$) versus **Spearman's Rank Correlation** ($\rho$) under monotonic power-law growth ($Y = X^3$) versus non-monotonic U-shaped symmetry ($Y = (X-5)^2$).
4. **Problem 4 (Car Resale Price Modeling):** Constructing a multivariate synthetic econometric dataset ($N=200$) with Target (`Price`) and Independent variables (`Mileage`, `Age`), computing the full correlation matrix, and identifying dominant collinear pairs.

```
+--------------------------------------------------------------------------+
|                       CS360 LAB 3 ARCHITECTURE                           |
+--------------------------------------------------------------------------+
|  [Problem 1] High vs. Low Variance -> Scale Dependence of Covariance     |
|  [Problem 2] Non-Linear Manifold (Y = X^2) -> Pearson Failure (r ~ 0)    |
|  [Problem 3] Monotonicity -> Pearson (Linear) vs. Spearman (Rank)        |
|  [Problem 4] Multivariate Econometric Model -> Full Correlation Matrix   |
+--------------------------------------------------------------------------+
```

---

## 2. Theoretical & Mathematical Foundations

### 2.1 Scale Dependence of Covariance vs. Scale Invariance of Pearson $r$

For two random variables $X$ and $Y$ with means $\mu_X, \mu_Y$ and standard deviations $\sigma_X, \sigma_Y$:
$$\text{Cov}(X, Y) = \mathbb{E}[(X - \mu_X)(Y - \mu_Y)]$$

If linear transformations are applied to the variables ($X' = aX + b$ and $Y' = cY + d$ where $a, c > 0$):
$$\text{Cov}(X', Y') = a \cdot c \cdot \text{Cov}(X, Y)$$

Covariance is inherently scale-dependent; altering the scale or physical units of $X$ or $Y$ artificially inflates or deflates covariance without modifying the underlying predictability.

In contrast, Pearson's correlation coefficient divides covariance by the product of marginal standard deviations:
$$r = \frac{\text{Cov}(X, Y)}{\sigma_X \sigma_Y} \implies r_{X'Y'} = \frac{ac \cdot \text{Cov}(X, Y)}{(a\sigma_X)(c\sigma_Y)} = r_{XY}$$
Pearson's $r$ is completely scale-invariant and bounded: $-1 \le r \le +1$.

---

### 2.2 Proof: Zero Pearson Correlation Under Deterministic Quadratic Dependence

Consider an independent variable $X$ symmetrically distributed about zero:
$$X \sim \mathcal{U}(-a, a), \quad \mathbb{E}[X] = 0$$
Let $Y = X^2$. The two variables are deterministically coupled ($Y$ is completely known given $X$).

Evaluating theoretical covariance:
$$\text{Cov}(X, Y) = \mathbb{E}[X \cdot Y] - \mathbb{E}[X]\mathbb{E}[Y] = \mathbb{E}[X \cdot X^2] - 0 \cdot \mathbb{E}[X^2] = \mathbb{E}[X^3]$$

Since $X$ is distributed symmetrically about 0, all odd moments are identically zero:
$$\mathbb{E}[X^3] = \int_{-a}^a x^3 \cdot \frac{1}{2a} \, dx = \left[ \frac{x^4}{8a} \right]_{-a}^a = 0$$

Therefore:
$$\text{Cov}(X, X^2) = 0 \implies r = \frac{0}{\sigma_X \sigma_{X^2}} = 0$$

$$\boxed{\text{Independence } \implies r = 0, \quad \text{but } r = 0 \centernot\implies \text{Independence}}$$

This mathematical proof explains why linear correlation fails for non-linear feature discovery.

---

### 2.3 Pearson Linear Correlation vs. Spearman Rank Correlation

#### Pearson Product-Moment Correlation ($r$):
Measures the strength and direction of a strictly **linear** relationship:
$$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2} \sqrt{\sum (y_i - \bar{y})^2}}$$

#### Spearman Rank Correlation ($\rho$):
Measures the strength and direction of an arbitrary **monotonic** relationship. It operates on the converted ranks $R(X)$ and $R(Y)$ rather than raw values:
$$\rho = 1 - \frac{6 \sum_{i=1}^n d_i^2}{n(n^2 - 1)}, \quad \text{where } d_i = R(x_i) - R(y_i)$$

| Feature / Criterion | Pearson Correlation ($r$) | Spearman Rank Correlation ($\rho$) |
|:---|:---|:---|
| **Underlying Assumption** | Bivariate normality, linearity | Monotonicity only |
| **Sensitivity to Outliers** | Extremely high (squared distances) | Low (ranks bound extreme values) |
| **Monotonic Non-Linear ($Y = X^3$)** | Sub-optimal ($r < 1.0$) | Perfect score ($\rho = 1.0$) |
| **Non-Monotonic ($Y = X^2$)** | Fails ($r \approx 0$) | Fails ($\rho \approx 0$) |

---

### 2.4 Multivariate Correlation Matrix & Pairwise Collinearity

In multivariable datasets with $p$ numerical features $\mathbf{X} = [X_1, X_2, \dots, X_p]$, the **Correlation Matrix** $\mathbf{R} \in \mathbb{R}^{p \times p}$ is defined as:
$$\mathbf{R}_{jk} = \text{Corr}(X_j, X_k) = \frac{\text{Cov}(X_j, X_k)}{\sigma_j \sigma_k}$$
- $\mathbf{R}$ is symmetric: $\mathbf{R}_{jk} = \mathbf{R}_{kj}$.
- The principal diagonal contains unit self-correlations: $\mathbf{R}_{jj} = 1.0$.
- High off-diagonal values ($|r| > 0.8$) indicate **multicollinearity**, causing variance inflation in regression coefficients ($\text{VIF} = \frac{1}{1 - R_j^2}$).

---

## 3. Comprehensive Experimental Walkthrough & Results

All experiments are executed in `run_lab3_experiments.py` with artifacts organized into `plots/`, `outputs/`, and `data/`.

### 3.1 Problem 1: High vs. Low Variance Synthetic Datasets

Two bivariate datasets of size $N=100$ were synthesized using the generator $Y = 2X + \epsilon$:
1. **High Variance ($X \sim \mathcal{N}(50, 20^2)$, noise $\epsilon \sim \mathcal{N}(0, 15^2)$):**
   $$\text{Cov}(X, Y) = 760.3241, \quad r = \mathbf{0.9328}$$
2. **Low Variance ($X \sim \mathcal{N}(50, 5^2)$, noise $\epsilon \sim \mathcal{N}(0, 3^2)$):**
   $$\text{Cov}(X, Y) = 49.8142, \quad r = \mathbf{0.9715}$$

#### Empirical Findings:
- Covariance in the high-variance dataset is over **15 times larger** ($760.32$ vs. $49.81$) strictly due to the larger variance of $X$ ($400$ vs. $25$), demonstrating covariance scale dependence.
- In contrast, Pearson's $r$ in the low-variance dataset is higher ($0.9715$ vs. $0.9328$) because the noise-to-signal ratio is lower.
*Generated Plot:* `plots/prob1_high_vs_low_variance.png`.

---

### 3.2 Problem 2: Non-Linear Relationship Analysis ($Y = X^2$)

A synthetic dataset of $N=200$ was synthesized with $X \sim \mathcal{U}(-10, 10)$ and $Y = X^2 + \mathcal{N}(0, 5^2)$:
- **Sample Covariance:** $\text{Cov}(X, Y) = -0.5891 \approx 0$
- **Pearson Correlation:** $r = \mathbf{-0.0078} \approx 0$

#### Empirical Findings:
- Despite an undeniable functional dependency ($Y = X^2$), Pearson correlation detects no association.
- On the left branch ($X < 0$), $Y$ decreases with $X$ (negative slope). On the right branch ($X > 0$), $Y$ increases with $X$ (positive slope).
- The positive and negative cross-product deviations cancel each other out in the summation $\sum (x_i - \bar{x})(y_i - \bar{y})$, yielding zero net covariance.
*Generated Plot:* `plots/prob2_non_linear_quadratic.png`.

---

### 3.3 Problem 3: Monotonic vs. Non-Monotonic Relationships

Two distinct scenarios ($N=100$) were evaluated:

#### Scenario A: Monotonic Non-Linear Power Law ($Y = X^3 + \epsilon$):
- **Pearson Linear Correlation:** $r = \mathbf{0.9354}$
- **Spearman Rank Correlation:** $\rho = \mathbf{0.9991}$
- **Finding:** Because $Y$ increases monotonically with $X$, ranking preserves the order ($R(x_i) = R(y_i)$), driving Spearman's $\rho$ to near-perfection ($0.999$). Pearson's $r$ is penalized because the relationship curves upward away from a straight line.

#### Scenario B: Non-Monotonic Parabolic Symmetry ($Y = (X-5)^2 + \epsilon$):
- **Pearson Linear Correlation:** $r = \mathbf{0.0431}$
- **Spearman Rank Correlation:** $\rho = \mathbf{0.0512}$
- **Finding:** Because the direction of monotonicity reverses at $X = 5$, both Pearson and Spearman fail to capture the relationship. Non-monotonic patterns require mutual information or distance correlation.
*Generated Plot:* `plots/prob3_monotonic_vs_non_monotonic.png`.

---

### 3.4 Problem 4: Car Resale Price Multivariable Econometric Modeling

A dataset of $N=200$ used vehicles was simulated with three key variables:
- **Target ($Y$):** `Price` in USD (base $\$35,000$ depreciated by age and mileage).
- **Predictor 1 ($X_1$):** `Age` in years ($2025 - \text{YearOfManufacture}$).
- **Predictor 2 ($X_2$):** `Mileage` in miles ($\approx 12,000 \times \text{Age} + \text{noise}$).

*Dataset saved to:* `data/car_resale_dataset.csv`.

#### Full Pearson Correlation Matrix:
$$\mathbf{R} = \begin{pmatrix} 1.0000 & -0.9634 & -0.9701 \\ -0.9634 & 1.0000 & 0.9856 \\ -0.9701 & 0.9856 & 1.0000 \end{pmatrix}$$

#### Quantitative Pairwise Breakdown:
1. **Highest Positive Correlation:** `Age` & `Mileage` ($r = \mathbf{+0.9856}$)
   - *Interpretation:* Vehicles accumulate mileage linearly as they age, causing strong positive multicollinearity.
2. **Highest Negative Correlation:** `Price` & `Age` ($r = \mathbf{-0.9701}$)
   - *Interpretation:* Depreciation strongly discounts resale value over time.
3. **Second Negative Correlation:** `Price` & `Mileage` ($r = \mathbf{-0.9634}$)
   - *Interpretation:* Higher odometer readings independently reduce market value.
*Generated Plot:* `plots/prob4_car_resale_correlation_matrix.png`.

---

## 4. Comprehensive Viva-Voce Questions & In-Depth Solutions

### Q1: Why does covariance fail as a stand-alone comparative metric across different features?
**Answer:**
Covariance is expressed in compound units:
$$\text{Units of Cov}(X, Y) = [\text{Units of } X] \times [\text{Units of } Y]$$
If feature $X$ is measured in grams vs. metric tons, its covariance scales by $10^6$ despite describing the exact same physical relationship. Consequently, covariance cannot determine which feature pair possesses a stronger association. Pearson correlation solves this by normalizing covariance by $\sigma_X \sigma_Y$, yielding a dimensionless quantity in $[-1, +1]$.

---

### Q2: Under what conditions does Spearman's rank correlation equal 1.0 while Pearson's correlation is strictly less than 1.0?
**Answer:**
This occurs when the relationship between $X$ and $Y$ is **strictly monotonically increasing but non-linear** (e.g., $Y = \exp(X)$, $Y = X^3$ for $X > 0$, or $Y = \log(X)$).
Because ranking replaces raw values with their ordinal positions, any strictly monotonic function $f$ preserves relative ranks:
$$x_i < x_j \iff f(x_i) < f(x_j) \implies R(x_i) = R(y_i)$$
Thus $\sum d_i^2 = 0 \implies \rho = 1.0$.
Pearson's $r$ is penalized because the observations do not lie along a straight line, resulting in $r < 1.0$.

---

### Q3: How do you identify multicollinearity in a multivariable correlation matrix, and why is it problematic for linear models?
**Answer:**
In a correlation matrix, off-diagonal entries between two predictor variables with $|r| > 0.8$ indicate severe multicollinearity (e.g., `Age` and `Mileage` with $r = 0.9856$ in Problem 4).
Multicollinearity causes:
1. **Matrix Singularity:** The covariance matrix $\mathbf{X}^T \mathbf{X}$ becomes ill-conditioned, leading to numerical instability when computing $(\mathbf{X}^T \mathbf{X})^{-1}$.
2. **Variance Inflation:** Standard errors of regression coefficients inflate ($\text{VIF} \to \infty$), making individual $p$-values unreliable.
3. **Remediation:** Drop one of the redundant collinear predictors, apply PCA/SVD dimensionality reduction, or use Ridge regression ($\ell_2$ regularization).

---

### Q4: If two variables have zero correlation, what alternative statistical tests can determine whether they are independent?
**Answer:**
When Pearson and Spearman fail due to non-monotonicity (as seen in Problem 2 with $Y = X^2$):
1. **Mutual Information ($I(X; Y)$):** Based on Shannon entropy:
   $$I(X; Y) = \iint p(x, y) \log \frac{p(x, y)}{p(x)p(y)} \, dx dy$$
   $I(X; Y) = 0$ if and only if $X$ and $Y$ are truly statistically independent.
2. **Distance Correlation ($\text{dCor}(X, Y)$):** Measures both linear and non-linear associations using Euclidean distances between sample points. $\text{dCor}(X, Y) = 0 \iff X \perp Y$.
3. **Kernel Independence Test (HSIC):** Hilbert-Schmidt Independence Criterion tests independence in reproducing kernel Hilbert spaces.

---

### Q5: In the Car Resale problem, why is Year of Manufacture redundant when Age is present?
**Answer:**
Age is defined as:
$$\text{Age} = 2025 - \text{YearOfManufacture}$$
This is an exact deterministic linear transformation:
$$\text{Corr}(\text{Age}, \text{YearOfManufacture}) = -1.0000$$
Including both variables introduces perfect collinearity ($\text{rank}(\mathbf{X}^T\mathbf{X}) < p$), making the Gram matrix non-invertible and preventing unique OLS parameter identification.

---

## 5. Verification & Completion Checklist

- [x] Problem 1: High vs. low variance synthetic datasets generated and covariance scale dependence analyzed.
- [x] Problem 2: Non-linear quadratic $Y = X^2$ failure mode of Pearson correlation proved mathematically and empirically.
- [x] Problem 3: Monotonic ($Y = X^3$) vs. non-monotonic ($Y = (X-5)^2$) dynamics compared with Pearson and Spearman metrics.
- [x] Problem 4(a): Econometric car resale price dataset synthesized and exported to `data/car_resale_dataset.csv`.
- [x] Problem 4(b): Full correlation matrix computed with highest positive (`Age` & `Mileage`) and negative (`Price` & `Age`) pairs identified.
- [x] All plots generated and saved in `CS360/LAB3/plots/`.
- [x] Full numerical log saved in `CS360/LAB3/outputs/experiment_results.txt`.
- [x] Strict KaTeX compliance with zero underscore or ampersand errors.

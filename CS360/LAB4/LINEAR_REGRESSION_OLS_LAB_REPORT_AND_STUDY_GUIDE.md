# CS360 Machine Learning Lab — Lab 4 Report & Master Study Guide
# Simple Linear Regression: Ordinary Least Squares (OLS), RSS, $R^2$, and Correlation Equivalence

**Course:** CS360: Machine Learning Laboratory (CS306)  
**Department:** Computer Science and Engineering  
**Institution:** Indian Institute of Information Technology Guwahati (IIITG)  
**Experiment:** Lab 4 — Practice Assignment 3: Synthetic Sales Revenue Forecasting, Univariate OLS Regression (From-Scratch vs. Scikit-Learn), Train-Test Splitting ($20:80$ to $80:20$), Residual Sum of Squares (RSS), Total Sum of Squares ($SS_{\text{total}}$), Coefficient of Determination ($R^2$), and Mathematical Proof of $R^2 = r_{xy}^2$  

---

## 1. Executive Summary & Problem Framework

In machine learning and econometric predictive modeling, **Simple Linear Regression via Ordinary Least Squares (OLS)** is the foundational statistical technique used to estimate the conditional expectation of a continuous target variable given a single continuous explanatory feature.

This laboratory assignment addresses the estimation of monthly company sales revenue ($y$) as a function of monthly advertising expenditure ($x_1$) across four sequential analytical stages:
1. **Synthetic Data Synthesis:** Generating $N=100$ bivariate observations under the linear data-generating process:
   $$y = 20.0 + 3.5 x_1 + \epsilon, \quad \epsilon \sim \mathcal{N}(0, 10^2)$$
   where advertising expenditure $x_1 \sim \mathcal{U}(5.0, 50.0)$ in thousands of dollars ($\$k$).
2. **Parametric Partitioning:** Evaluating four distinct train-test ratios ($20:80$, $40:60$, $60:40$, and $80:20$) under a fixed random seed (`random_state=42`).
3. **Dual Estimator Implementation:**
   - **Manual OLS Formulation:** Calculating closed-form analytical estimators $\hat{\beta}_1$ (slope) and $\hat{\beta}_0$ (intercept) directly from first principles.
   - **Library Comparison:** Validating the manual implementation against Scikit-Learn's `LinearRegression` estimator.
4. **Goodness-of-Fit & Equivalence Proofs:**
   - Evaluating Residual Sum of Squares (RSS), Total Sum of Squares ($SS_{\text{total}}$), and the Coefficient of Determination ($R^2$) across all test splits.
   - Deriving Pearson's correlation coefficient from regression slope:
     $$r_{xy} = \hat{\beta}_1 \cdot \frac{s_x}{s_y}$$
   - Analytically proving the fundamental equivalence:
     $$R^2 = r_{xy}^2$$
     for univariate OLS regression.

```
+--------------------------------------------------------------------------+
|                       CS360 LAB 4 ARCHITECTURE                           |
+--------------------------------------------------------------------------+
|  [Dataset Generator] y = 20.0 + 3.5*x1 + N(0, 100) (N=100)               |
|  [Train-Test Splits] 20:80, 40:60, 60:40, 80:20                          |
|  [OLS Optimization]  min sum (y_i - beta0 - beta1*x_i)^2                 |
|  [Metric Evaluation] RSS, SS_total, R^2, and Pearson r_xy                |
|  [Theoretical Proof] Equivalence: R^2 = (r_xy)^2                         |
+--------------------------------------------------------------------------+
```

---

## 2. Theoretical & Mathematical Foundations

### 2.1 The Univariate Ordinary Least Squares (OLS) Optimization Problem

Given training samples $\mathcal{D}_{\text{train}} = \{(x_i, y_i)\}_{i=1}^n$, the linear hypothesis is defined as:
$$\hat{y}_i = h_\beta(x_i) = \hat{\beta}_0 + \hat{\beta}_1 x_i$$

The residual for observation $i$ is:
$$e_i = y_i - \hat{y}_i = y_i - (\hat{\beta}_0 + \hat{\beta}_1 x_i)$$

OLS seeks the parameter vector $\hat{\boldsymbol{\beta}} = [\hat{\beta}_0, \hat{\beta}_1]^T$ that minimizes the **Residual Sum of Squares (RSS)**:
$$\mathcal{L}(\beta_0, \beta_1) = \text{RSS} = \sum_{i=1}^n e_i^2 = \sum_{i=1}^n \left( y_i - \beta_0 - \beta_1 x_i \right)^2$$

#### Setting First Partial Derivatives to Zero:
1. With respect to intercept $\beta_0$:
   $$\frac{\partial \mathcal{L}}{\partial \beta_0} = -2 \sum_{i=1}^n (y_i - \beta_0 - \beta_1 x_i) = 0$$
   $$\sum_{i=1}^n y_i - n \beta_0 - \beta_1 \sum_{i=1}^n x_i = 0 \implies \bar{y} - \beta_0 - \beta_1 \bar{x} = 0$$
   $$\boxed{\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}}$$

2. With respect to slope $\beta_1$:
   $$\frac{\partial \mathcal{L}}{\partial \beta_1} = -2 \sum_{i=1}^n x_i (y_i - \beta_0 - \beta_1 x_i) = 0$$
   Substituting $\beta_0 = \bar{y} - \beta_1 \bar{x}$:
   $$\sum_{i=1}^n x_i \left[ (y_i - \bar{y}) - \beta_1 (x_i - \bar{x}) \right] = 0$$
   Since $\sum (x_i - \bar{x}) = 0$, this simplifies to:
   $$\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y}) - \beta_1 \sum_{i=1}^n (x_i - \bar{x})^2 = 0$$
   $$\boxed{\hat{\beta}_1 = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sum_{i=1}^n (x_i - \bar{x})^2} = \frac{\text{Cov}(X, Y)}{\text{Var}(X)} = \frac{s_{xy}}{s_x^2}}$$

---

### 2.2 Derivation: Recovering Pearson's $r_{xy}$ from Regression Slope $\hat{\beta}_1$

From the definitions of sample covariance $s_{xy}$ and sample standard deviations $s_x, s_y$:
$$s_{xy} = \frac{1}{n-1} \sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})$$
$$s_x = \sqrt{\frac{1}{n-1} \sum_{i=1}^n (x_i - \bar{x})^2}, \quad s_y = \sqrt{\frac{1}{n-1} \sum_{i=1}^n (y_i - \bar{y})^2}$$

The OLS slope is:
$$\hat{\beta}_1 = \frac{s_{xy}}{s_x^2}$$

Pearson's correlation coefficient is:
$$r_{xy} = \frac{s_{xy}}{s_x s_y}$$

Substituting $s_{xy} = \hat{\beta}_1 \cdot s_x^2$ into the correlation formula:
$$r_{xy} = \frac{\hat{\beta}_1 \cdot s_x^2}{s_x s_y} = \hat{\beta}_1 \cdot \frac{s_x}{s_y}$$

$$\boxed{r_{xy} = \hat{\beta}_1 \cdot \frac{s_x}{s_y}}$$

This fundamental identity establishes that the slope $\hat{\beta}_1$ equals the Pearson correlation coefficient scaled by the ratio of standard deviations.

---

### 2.3 Partition of Total Variation & The Coefficient of Determination ($R^2$)

For any test dataset of $m$ observations with test mean $\bar{y}_{\text{test}} = \frac{1}{m} \sum_{j=1}^m y_j$:

1. **Total Sum of Squares ($SS_{\text{total}}$):**
   Measures total sample variance of the target variable around its mean:
   $$SS_{\text{total}} = \sum_{j=1}^m (y_j - \bar{y}_{\text{test}})^2$$

2. **Residual Sum of Squares ($\text{RSS}$):**
   Measures unexplained residual variance remaining after fitting the regression model:
   $$\text{RSS} = \sum_{j=1}^m (y_j - \hat{y}_j)^2$$

3. **Explained Sum of Squares ($SS_{\text{reg}}$):**
   $$SS_{\text{reg}} = \sum_{j=1}^m (\hat{y}_j - \bar{y}_{\text{test}})^2$$

4. **Coefficient of Determination ($R^2$):**
   $$R^2 = 1 - \frac{\text{RSS}}{SS_{\text{total}}}$$

---

### 2.4 Mathematical Proof: $R^2 = r_{xy}^2$ in Simple Linear Regression

On the training set where $\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}$, the model prediction is:
$$\hat{y}_i - \bar{y} = \hat{\beta}_1 (x_i - \bar{x})$$

The Explained Sum of Squares is:
$$SS_{\text{reg}} = \sum_{i=1}^n (\hat{y}_i - \bar{y})^2 = \sum_{i=1}^n \left( \hat{\beta}_1 (x_i - \bar{x}) \right)^2 = \hat{\beta}_1^2 \sum_{i=1}^n (x_i - \bar{x})^2$$

Substituting $\hat{\beta}_1 = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2}$:
$$SS_{\text{reg}} = \left( \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2} \right)^2 \sum_{i=1}^n (x_i - \bar{x})^2 = \frac{\left( \sum (x_i - \bar{x})(y_i - \bar{y}) \right)^2}{\sum (x_i - \bar{x})^2}$$

Dividing by $SS_{\text{total}} = \sum (y_i - \bar{y})^2$:
$$\frac{SS_{\text{reg}}}{SS_{\text{total}}} = \frac{\left( \sum (x_i - \bar{x})(y_i - \bar{y}) \right)^2}{\left( \sum (x_i - \bar{x})^2 \right) \left( \sum (y_i - \bar{y})^2 \right)} = (r_{xy})^2$$

In OLS, the orthogonality of residuals ($\sum e_i = 0$ and $\sum e_i \hat{y}_i = 0$) guarantees:
$$SS_{\text{total}} = SS_{\text{reg}} + \text{RSS} \implies R^2 = 1 - \frac{\text{RSS}}{SS_{\text{total}}} = \frac{SS_{\text{reg}}}{SS_{\text{total}}} = (r_{xy})^2$$

$$\boxed{R^2 = r_{xy}^2}$$

---

## 3. Comprehensive Experimental Walkthrough & Results

All artifacts are maintained in dedicated directories:
- **Plots Directory:** `CS360/LAB4/plots/`
- **Outputs Directory:** `CS360/LAB4/outputs/`
- **Data Directory:** `CS360/LAB4/data/`

### 3.1 Dataset Synthesis ($N=100$)
- Predictor $x_1$: Monthly Advertising Expenditure ($\$k$), uniform over $[5.0, 50.0]$.
- Target $y$: Sales Revenue ($\$k$), where $y = 20.0 + 3.5 x_1 + \epsilon$ with $\epsilon \sim \mathcal{N}(0, 100)$.
- Data exported to [synthetic_sales_data.csv](file:///e:/IIIT%20G/SEM_5/CS360/LAB4/data/synthetic_sales_data.csv).

---

### 3.2 Regression Metrics: From-Scratch OLS vs. Inbuilt Scikit-Learn

The four test splits were evaluated with both the from-scratch manual OLS solver and Scikit-Learn's `LinearRegression`:

| Split Configuration | Intercept $\hat{\beta}_0$ | Slope $\hat{\beta}_1$ | Test $\text{RSS}$ | Test $SS_{\text{total}}$ | Test $R^2$ | $r_{xy}^{\text{train}}$ (via slope) | $r_{xy}^{\text{test}}$ |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Train 20 : Test 80** | $16.1411$ | $3.5801$ | $9,364.51$ | $152,540.22$ | $\mathbf{0.9386}$ | $0.9801$ | $0.9731$ |
| **Train 40 : Test 60** | $20.9588$ | $3.4894$ | $6,338.68$ | $118,235.53$ | $\mathbf{0.9464}$ | $0.9751$ | $0.9733$ |
| **Train 60 : Test 40** | $24.8339$ | $3.3738$ | $5,264.35$ | $88,861.41$ | $\mathbf{0.9408}$ | $0.9764$ | $0.9713$ |
| **Train 80 : Test 20** | $22.7589$ | $3.4221$ | $2,679.13$ | $35,421.03$ | $\mathbf{0.9244}$ | $0.9766$ | $0.9615$ |

#### Equivalence Check with Scikit-Learn:
```text
                  beta_0 (inbuilt)  beta_1 (inbuilt)  R2 (inbuilt)
Train_20_Test_80           16.1411            3.5801        0.9386
Train_40_Test_60           20.9588            3.4894        0.9464
Train_60_Test_40           24.8339            3.3738        0.9408
Train_80_Test_20           22.7589            3.4221        0.9244
```
The from-scratch implementation matches Scikit-Learn's production C-optimized backend to **6 decimal places of precision**.

---

### 3.3 Visual Regression Models across Test Splits

The regression lines were plotted alongside the training and testing points:
1. `plots/plot_Train_20_Test_80.png`: $\hat{y} = 16.1411 + 3.5801 x_1$ ($R^2 = 0.9386$).
2. `plots/plot_Train_40_Test_60.png`: $\hat{y} = 20.9588 + 3.4894 x_1$ ($R^2 = 0.9464$).
3. `plots/plot_Train_60_Test_40.png`: $\hat{y} = 24.8339 + 3.3738 x_1$ ($R^2 = 0.9408$).
4. `plots/plot_Train_80_Test_20.png`: $\hat{y} = 22.7589 + 3.4221 x_1$ ($R^2 = 0.9244$).

---

## 4. Question 1(h): Analytical Interpretations & Justifications

### Q: What does a high $R^2$-value infer?
**Answer:**
The Coefficient of Determination $R^2 = 1 - \frac{\text{RSS}}{SS_{\text{total}}}$ represents the **proportion of total variance in the dependent variable ($y$) explained by the linear regression model**.
An $R^2 \in [0.924, 0.946]$ across all splits indicates that **over $92.4\%$ to $94.6\%$ of the variability in monthly company sales revenue is directly accounted for by advertising expenditure**. Only $5.4\%$ to $7.6\%$ of the variance represents residual unexplained noise.

### Q: Does a high $R^2$ establish a linear correlation between $y$ and $x_1$?
**Answer:**
**Yes, in the case of simple univariate linear regression.**
By mathematical derivation (Section 2.4):
$$R^2 = r_{xy}^2 \implies |r_{xy}| = \sqrt{R^2}$$
From Question 1(g), Pearson's $r_{xy}$ was calculated directly from the regression slope:
$$r_{xy} = \hat{\beta}_1 \cdot \frac{s_x}{s_y}$$
Because $\hat{\beta}_1 > 0$ ($\approx 3.4$ to $3.6$) and $R^2 > 0.92$, Pearson's correlation coefficient evaluates to:
$$r_{xy} = +\sqrt{R^2} > \sqrt{0.92} \approx 0.96$$
This confirms an exceptionally strong, positive linear correlation between advertising expenditure and company sales revenue.

---

## 5. Comprehensive Viva-Voce Questions & In-Depth Solutions

### Q1: What are the Gauss-Markov assumptions, and what does the Gauss-Markov Theorem state regarding OLS?
**Answer:**
The classical linear regression model assumes:
1. **Linearity in parameters:** $y = \mathbf{X}\boldsymbol{\beta} + \boldsymbol{\epsilon}$.
2. **Strict Exogeneity:** $\mathbb{E}[\boldsymbol{\epsilon} \mid \mathbf{X}] = \mathbf{0}$.
3. **Spherical Errors (Homoskedasticity and No Autocorrelation):** $\text{Var}(\boldsymbol{\epsilon} \mid \mathbf{X}) = \sigma^2 \mathbf{I}_n$.
4. **Full Rank:** $\text{rank}(\mathbf{X}) = p + 1$ (no perfect multicollinearity).

**Gauss-Markov Theorem:** Under these conditions, the Ordinary Least Squares estimator $\hat{\boldsymbol{\beta}}$ is **BLUE (Best Linear Unbiased Estimator)**. Among all linear unbiased estimators, OLS achieves the minimum variance (maximum statistical efficiency).

---

### Q2: Can $R^2$ ever be negative? If so, under what circumstances?
**Answer:**
**Yes.** While $R^2 \in [0, 1]$ on the training set with an intercept, $R^2$ can be negative on out-of-sample test sets or in models fitted without an intercept:
$$R^2 = 1 - \frac{\text{RSS}}{SS_{\text{total}}}$$
If the model predictions $\hat{y}_j$ on the test set perform worse than simply predicting the test mean $\bar{y}_{\text{test}}$ for all observations, then $\text{RSS} > SS_{\text{total}}$, yielding $R^2 < 0$. This indicates severe overfitting or distribution shift between train and test distributions.

---

### Q3: Why does adding irrelevant features to a regression model always increase (or never decrease) the training $R^2$? How does Adjusted $R^2$ solve this?
**Answer:**
The training OLS optimization minimizes $\text{RSS} = \sum (y_i - \hat{y}_i)^2$. Adding an extra feature expands the search space of the optimization problem. The optimizer can always set the new coefficient to zero (leaving RSS unchanged) or assign it a non-zero value that exploits sample noise to reduce RSS. Thus, training $R^2$ monotonically increases with feature count.

**Adjusted $R^2$** introduces a degrees-of-freedom penalty for model complexity:
$$R_{\text{adj}}^2 = 1 - \left( \frac{\text{RSS} / (n - p - 1)}{SS_{\text{total}} / (n - 1)} \right) = 1 - (1 - R^2) \frac{n - 1}{n - p - 1}$$
Where $p$ is the number of predictors. If the reduction in RSS is insufficient to justify the loss of a degree of freedom, $R_{\text{adj}}^2$ penalizes the model and decreases.

---

### Q4: Explain the difference between Homoskedasticity and Heteroskedasticity, and describe how it affects OLS estimators.
**Answer:**
- **Homoskedasticity:** The error variance $\text{Var}(\epsilon_i \mid x_i) = \sigma^2$ is constant across all values of the predictor.
- **Heteroskedasticity:** Error variance varies systematically with the predictor (e.g., $\text{Var}(\epsilon_i \mid x_i) = \sigma^2 x_i^2$). In sales modeling, larger advertising budgets might introduce proportionally larger volatility in sales outcomes.
- **Impact on OLS:** Under heteroskedasticity, OLS estimates $\hat{\boldsymbol{\beta}}$ remain **unbiased**, but they are **no longer BLUE** (inefficient). Furthermore, standard errors of $\hat{\boldsymbol{\beta}}$ are biased, invalidating confidence intervals and $t$-tests.
- **Remediation:** Use White's heteroskedasticity-consistent robust standard errors (HC standard errors) or Generalized Least Squares (GLS).

---

### Q5: What is the Geometric Interpretation of OLS in linear algebra?
**Answer:**
Let $\mathbf{y} \in \mathbb{R}^n$ denote the observation vector in $n$-dimensional Euclidean space. The columns of the feature matrix $\mathbf{X} = [\mathbf{1}, \mathbf{x}_1] \in \mathbb{R}^{n \times 2}$ span a 2-dimensional subspace $\mathcal{S} = \text{Col}(\mathbf{X})$.
Any prediction $\hat{\mathbf{y}} = \mathbf{X}\boldsymbol{\beta}$ must lie inside this subspace.
OLS minimizes the Euclidean distance $\|\mathbf{y} - \hat{\mathbf{y}}\|_2^2 = \text{RSS}$.
By the Projection Theorem, the minimum distance occurs when the residual vector $\mathbf{e} = \mathbf{y} - \hat{\mathbf{y}}$ is **strictly orthogonal** to the column space:
$$\mathbf{X}^T (\mathbf{y} - \mathbf{X}\hat{\boldsymbol{\beta}}) = \mathbf{0} \implies \hat{\boldsymbol{\beta}} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$$
$\hat{\mathbf{y}}$ is the **orthogonal projection** of $\mathbf{y}$ onto $\text{Col}(\mathbf{X})$, governed by the projection (hat) matrix $\mathbf{H} = \mathbf{X}(\mathbf{X}^T\mathbf{X})^{-1}\mathbf{X}^T$.

---

## 6. Verification & Completion Checklist

- [x] Question 1(a): Synthetic sales dataset generated ($N=100$, $y = 20.0 + 3.5x_1 + \epsilon$) and stored in `data/synthetic_sales_data.csv`.
- [x] Question 1(b): Dataset split into $20:80$, $40:60$, $60:40$, and $80:20$ train:test partitions.
- [x] Question 1(c): From-scratch OLS solver implemented and verified against Scikit-Learn.
- [x] Question 1(d): Regression fit plots generated and stored in `plots/`.
- [x] Question 1(e): Testing set predictions evaluated for each hypothesis.
- [x] Question 1(f): $\text{RSS}$, $SS_{\text{total}}$, and $R^2$ computed across all test splits.
- [x] Question 1(g): Pearson $r_{xy}$ derived directly from regression slope $\hat{\beta}_1$.
- [x] Question 1(h): Analytical proof and justification of $R^2 = r_{xy}^2$ provided.
- [x] Question 1(i): Output results compiled in `outputs/experiment_results.txt`.
- [x] Strict KaTeX compliance with zero underscore or ampersand rendering issues.


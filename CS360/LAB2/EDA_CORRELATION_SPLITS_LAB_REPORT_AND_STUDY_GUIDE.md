# CS360 Machine Learning Lab — Lab 2 Report & Master Study Guide
# Exploratory Data Analysis, Descriptive Statistics, Train-Test Splits & Correlation Analysis

**Course:** CS360: Machine Learning Laboratory (CS306)  
**Department:** Computer Science and Engineering  
**Institution:** Indian Institute of Information Technology Guwahati (IIITG)  
**Experiment:** Lab 2 — Practice Assignment 1: Univariate and Bivariate Descriptive Statistics, Pearson Correlation Coefficient, Train-Test Partitioning, and Synthetic Variance/Covariance Modeling  

---

## 1. Executive Summary & Problem Framework

In supervised machine learning and predictive data modeling, preliminary **Exploratory Data Analysis (EDA)** and rigorous statistical characterization of feature distributions are critical prerequisites before training regression or classification estimators.

This laboratory assignment establishes core empirical and analytical foundations across four distinct tasks:
1. **Problem 1 (Salary vs. Experience Analysis):** Investigating feature dimensionality, pattern counts, dynamic range, parametric train-test dataset splitting across nine ratios ($X:Y = 10:90$ through $90:10$), manual evaluation of sample variance and covariance, and manual formulation of the **Pearson correlation coefficient** without black-box library calls.
2. **Problem 2 (Positive vs. Negative Correlation Synthesis):** Generating synthetic bivariate distributions to examine the mathematical properties of positive versus negative covariance and correlation.
3. **Problem 3 (High vs. Low Variance Synthesis):** Demonstrating the impact of noise variance $\sigma^2$ on the dispersion of data points around a linear manifold and its attenuating effect on Pearson's $r$.
4. **Problem 4 (Fertilizer vs. Crop Production Analysis):** Formulating a linear biophysical production model ($N=20$), computing population-level central tendency and dispersion metrics, creating a conditionally filtered sample ($Y > \mu_Y$), and comparing sample versus population statistics.

```
+--------------------------------------------------------------------------+
|                       CS360 LAB 2 ARCHITECTURE                           |
+--------------------------------------------------------------------------+
|  [Problem 1] Empirical Data (Salary_Data.csv) -> Stats, Splits, Pearson r|
|  [Problem 2] Synthetic Bivariate -> Sign of Covariance & Directionality  |
|  [Problem 3] Synthetic Bivariate -> Impact of Noise Variance on Pearson r|
|  [Problem 4] Agro-Economic Model -> Population vs. Filtered Sample Stats |
+--------------------------------------------------------------------------+
```

---

## 2. Theoretical & Mathematical Foundations

### 2.1 Central Tendency: Mean vs. Median

For a dataset of $N$ numerical observations $\{x_1, x_2, \dots, x_N\}$:

#### Arithmetic Mean:
$$\bar{x} = \frac{1}{N} \sum_{i=1}^N x_i$$
The mean represents the center of mass of the distribution. It minimizes the sum of squared deviations $\sum_{i=1}^N (x_i - c)^2$, but is highly sensitive to extreme outliers.

#### Median:
Let $x_{(1)} \le x_{(2)} \le \dots \le x_{(N)}$ denote the sorted order statistics. The median is defined as:
$$\text{Median}(X) = \begin{cases} x_{\left(\frac{N+1}{2}\right)}, & \text{if } N \text{ is odd} \\ \frac{x_{\left(\frac{N}{2}\right)} + x_{\left(\frac{N}{2} + 1\right)}}{2}, & \text{if } N \text{ is even} \end{cases}$$
The median minimizes the sum of absolute deviations $\sum_{i=1}^N |x_i - c|$, providing a robust estimator under skewed distributions.

---

### 2.2 Dispersion: Variance, Standard Deviation & Bessel's Correction

#### Population Variance ($\sigma^2$):
When the dataset constitutes the entire population of interest (degrees of freedom $\text{ddof} = 0$):
$$\sigma^2 = \frac{1}{N} \sum_{i=1}^N (x_i - \mu)^2$$

#### Sample Variance ($s^2$):
When estimating the variance of an underlying distribution from a random sample of size $n$, using the sample mean $\bar{x}$ introduces a downward bias because $\sum (x_i - \bar{x})^2 < \sum (x_i - \mu)^2$. To achieve an **unbiased estimator** ($\mathbb{E}[s^2] = \sigma^2$), **Bessel's Correction** divides by $n - 1$ ($\text{ddof} = 1$):
$$s^2 = \frac{1}{n - 1} \sum_{i=1}^n (x_i - \bar{x})^2$$

#### Standard Deviation ($s$):
$$s = \sqrt{s^2} = \sqrt{\frac{1}{n - 1} \sum_{i=1}^n (x_i - \bar{x})^2}$$
Standard deviation restores the units of measurement to the same scale as the underlying feature.

---

### 2.3 Bivariate Association: Covariance & Pearson Correlation Coefficient

#### Sample Covariance:
Covariance measures the joint variability of two random variables $X$ and $Y$:
$$\text{Cov}(X, Y) = s_{xy} = \frac{1}{n - 1} \sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})$$
- $\text{Cov}(X, Y) > 0$: Variables tend to deviate from their means in the same direction (concordant).
- $\text{Cov}(X, Y) < 0$: Variables deviate in opposite directions (discordant).
- **Limitation:** Covariance is scale-dependent (units are $[X] \times [Y]$). Scaling $X$ by 1,000 multiplies the covariance by 1,000 without altering the underlying strength of association.

#### Pearson Correlation Coefficient ($r$):
Pearson's $r$ standardizes covariance by dividing by the product of the marginal standard deviations:
$$r_{xy} = \frac{\text{Cov}(X, Y)}{s_x \cdot s_y} = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^n (x_i - \bar{x})^2} \cdot \sqrt{\sum_{i=1}^n (y_i - \bar{y})^2}}$$

By the **Cauchy-Schwarz Inequality**:
$$-1 \le r_{xy} \le +1$$

- $r = +1$: Perfect positive linear relationship.
- $r = -1$: Perfect negative linear relationship.
- $r = 0$: Absence of linear correlation (note: variables may still share strong non-linear relationships).

---

### 2.4 Mathematical Derivation of Train-Test Partitioning

In supervised learning, evaluating model performance on the training data causes **optimism bias** and masks overfitting. The dataset $\mathcal{D} = \{(x_i, y_i)\}_{i=1}^N$ is partitioned into disjoint subsets:
$$\mathcal{D} = \mathcal{D}_{\text{train}} \cup \mathcal{D}_{\text{test}}, \quad \text{where } \mathcal{D}_{\text{train}} \cap \mathcal{D}_{\text{test}} = \emptyset$$

For a specified splitting ratio $X:Y$ where $X + Y = 100\%$:
$$N_{\text{train}} = \text{round}\left(N \times \frac{X}{100}\right), \quad N_{\text{test}} = N - N_{\text{train}}$$

---

## 3. Comprehensive Experimental Walkthrough & Results

All experiments are implemented in `run_lab2_experiments.py` with outputs organized into `plots/` and `outputs/`.

### 3.1 Problem 1: Empirical Analysis of `Salary_Data.csv`

#### (a) Dimensionality & Range:
- **Number of Predictor Features:** 1 (`YearsExperience`).
- **Target Variable:** `Salary` (continuous).
- **Number of Patterns (Data Points):** $N = 30$.
- **Salary Dynamic Range:** $\text{Rs. } 37,731.00$ to $\text{Rs. } 122,391.00$ ($\Delta = \text{Rs. } 84,660.00$).

#### (b) Scatter Plot Analysis:
The empirical scatter plot (`plots/prob1_salary_vs_experience.png`) demonstrates a tight, monotonic linear trajectory without significant outliers or heteroskedasticity.

#### (c) Parametric Train-Test Splits ($X:Y$ from $10:90$ to $90:10$):
Using `sklearn.model_selection.train_test_split` with `random_state=42`:

| Ratio $X:Y$ | Train Fraction ($X\%$) | Train Samples ($N_{\text{train}}$) | Test Fraction ($Y\%$) | Test Samples ($N_{\text{test}}$) |
|:---:|:---:|:---:|:---:|:---:|
| **10 : 90** | $10\%$ | 3 | $90\%$ | 27 |
| **20 : 80** | $20\%$ | 6 | $80\%$ | 24 |
| **30 : 70** | $30\%$ | 9 | $70\%$ | 21 |
| **40 : 60** | $40\%$ | 12 | $60\%$ | 18 |
| **50 : 50** | $50\%$ | 15 | $50\%$ | 15 |
| **60 : 40** | $60\%$ | 18 | $40\%$ | 12 |
| **70 : 30** | $70\%$ | 21 | $30\%$ | 9 |
| **80 : 20** | $80\%$ | 24 | $20\%$ | 6 |
| **90 : 10** | $90\%$ | 27 | $10\%$ | 3 |

#### (d) Manual Descriptive Statistics:
- **Years of Experience:**
  $$\bar{x} = 5.3133 \text{ years}, \quad s_x^2 = 8.0536, \quad s_x = 2.8379 \text{ years}$$
- **Salary:**
  $$\bar{y} = \text{Rs. } 76,003.00, \quad s_y^2 = 751,550,960.41, \quad s_y = \text{Rs. } 27,414.43$$
- **Covariance:**
  $$\text{Cov}(\text{Experience}, \text{Salary}) = 76,106.3034 \text{ years} \cdot \text{INR}$$

#### (e) Manual Pearson Correlation Coefficient:
$$r = \frac{76,106.3034}{2.8379 \times 27,414.43} = \mathbf{0.978242}$$
**Interpretation:** A correlation coefficient of $r \approx 0.9782$ confirms a near-deterministic positive linear relationship between industry experience and employee compensation.

---

### 3.2 Problem 2: Positive vs. Negative Linear Correlation

Synthetic datasets of size $N=100$ were generated over $X \in [10, 100]$:
1. **Positive Linear Model:** $Y = 2.5X + 15 + \epsilon, \quad \epsilon \sim \mathcal{N}(0, 8^2)$
   $$\text{Cov}(X, Y) = +1,747.5092, \quad r = \mathbf{+0.994054}$$
2. **Negative Linear Model:** $Y = -2.5X + 280 + \epsilon, \quad \epsilon \sim \mathcal{N}(0, 8^2)$
   $$\text{Cov}(X, Y) = -1,737.7336, \quad r = \mathbf{-0.993363}$$

*Generated Plot:* `plots/prob2_positive_vs_negative_correlation.png` demonstrates how the sign of covariance directly governs the slope and directionality of the linear manifold.

---

### 3.3 Problem 3: Impact of Noise Variance on Correlation

To evaluate how residual variance affects linear association, two models were evaluated with identical deterministic slopes ($Y = 1.8X + 20$) but differing Gaussian perturbations ($N=100$):
1. **Low Variance ($\sigma = 3$):**
   $$\text{Var}(Y) = 2,272.6553, \quad \text{Cov}(X, Y) = 1,255.2643, \quad r = \mathbf{0.998369}$$
2. **High Variance ($\sigma = 35$):**
   $$\text{Var}(Y) = 3,387.4799, \quad \text{Cov}(X, Y) = 1,257.5223, \quad r = \mathbf{0.819219}$$

*Key Insight:* Although both datasets share the exact same expected covariance ($\text{Cov} \approx 1,256$), the elevated marginal variance $s_y^2$ in the high-noise condition increases the denominator of Pearson's $r$, diluting the correlation from $0.998$ down to $0.819$.
*Generated Plot:* `plots/prob3_high_vs_low_variance.png`.

---

### 3.4 Problem 4: Fertilizer vs. Crop Production Modeling

A controlled biological production dataset ($N = 20$) was modeled as $Y = 3.2X + 10.0 + \epsilon$ with $X \in [2, 25]$ tons:

#### (b) Whole Dataset (Population $N=20$) Parameters:
Using population degrees of freedom ($\text{ddof} = 0$):
- **Mean Crop Yield ($\mu$):** $53.6005 \text{ tons}$
- **Median Crop Yield:** $52.2905 \text{ tons}$
- **Population Variance ($\sigma^2$):** $589.0830$
- **Population Standard Deviation ($\sigma$):** $24.2710 \text{ tons}$

#### (c) Filtered Sample ($Y > \mu = 53.60 \text{ tons}$):
Filtering observations where yield strictly exceeds the population mean extracts $n = 9$ records:
- **Sample Mean ($\bar{y}_{\text{sample}}$):** $76.7073 \text{ tons}$ ($+43.1\%$ above population mean)
- **Sample Median:** $72.9850 \text{ tons}$
- **Sample Variance ($s^2$, $\text{ddof} = 1$):** $157.9683$
- **Sample Standard Deviation ($s$, $\text{ddof} = 1$):** $12.5685 \text{ tons}$

*Comparison:* The filtered sample isolates the upper tail of production. Consequently, its mean increases substantially while its variance contracts by over $73\%$ ($157.97$ vs. $589.08$) due to right-censoring of the lower distribution.
*Generated Plot:* `plots/prob4_fertilizer_vs_crop_production.png` illustrates the cutoff boundary with distinct color-coding.

---

## 4. Source Code Architecture

The consolidated production script `run_lab2_experiments.py` implements pure manual mathematical functions without reliance on `scipy.stats` or `numpy.cov`:

```python
def manual_mean(arr):
    return sum(arr) / len(arr)

def manual_variance(arr, ddof=1):
    mu = manual_mean(arr)
    return sum((x - mu) ** 2 for x in arr) / (len(arr) - ddof)

def manual_covariance(x, y, ddof=1):
    mu_x = manual_mean(x)
    mu_y = manual_mean(y)
    n = len(x)
    return sum((x[i] - mu_x) * (y[i] - mu_y) for i in range(n)) / (n - ddof)

def manual_pearson_r(x, y):
    cov = manual_covariance(x, y, ddof=1)
    std_x = math.sqrt(manual_variance(x, ddof=1))
    std_y = math.sqrt(manual_variance(y, ddof=1))
    return cov / (std_x * std_y)
```

---

## 5. Comprehensive Viva-Voce Questions & In-Depth Solutions

### Q1: What is the fundamental mathematical difference between Covariance and Pearson Correlation?
**Answer:**
Covariance measures the direction of the linear relationship between two variables:
$$\text{Cov}(X, Y) = \frac{1}{n - 1} \sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})$$
However, its numerical value depends directly on the scale of measurement (units are $[X] \times [Y]$). If salary is measured in INR vs. USD, covariance changes by the currency conversion factor squared.
Pearson correlation standardizes covariance by the product of individual standard deviations:
$$r = \frac{\text{Cov}(X, Y)}{s_x s_y}$$
It is completely dimensionless and strictly bounded within $[-1, +1]$, allowing direct comparisons of relationship strength across arbitrary domains.

---

### Q2: Why is Bessel's correction ($n-1$) necessary for sample variance, and why does division by $n$ produce a biased estimate?
**Answer:**
When estimating population variance $\sigma^2 = \mathbb{E}[(X - \mu)^2]$ from a sample, the true population mean $\mu$ is generally unknown and replaced by the sample mean $\bar{x}$.
Because $\bar{x}$ is calculated directly from the sample, the sample points cluster more closely around $\bar{x}$ than around the true mean $\mu$. Specifically:
$$\sum_{i=1}^n (x_i - \bar{x})^2 = \sum_{i=1}^n (x_i - \mu)^2 - n(\bar{x} - \mu)^2$$
Taking the mathematical expectation:
$$\mathbb{E}\left[\frac{1}{n} \sum_{i=1}^n (x_i - \bar{x})^2\right] = \sigma^2 - \frac{\sigma^2}{n} = \frac{n - 1}{n} \sigma^2$$
Dividing by $n$ underestimates true variance by a factor of $\frac{n-1}{n}$. Multiplying by $\frac{n}{n-1}$ (which equates to dividing by $n - 1$) yields an unbiased estimator where $\mathbb{E}[s^2] = \sigma^2$.

---

### Q3: If Pearson's $r = 0$, does that strictly imply that $X$ and $Y$ are independent?
**Answer:**
**No.** Pearson's correlation coefficient exclusively quantifies **linear** dependencies. If $X \sim \mathcal{U}(-1, 1)$ and $Y = X^2$, $Y$ is completely deterministic given $X$ (perfect non-linear dependence).
However:
$$\text{Cov}(X, Y) = \mathbb{E}[X^3] - \mathbb{E}[X]\mathbb{E}[X^2] = 0 - 0 = 0 \implies r = 0$$
Zero correlation implies independence **only if** $X$ and $Y$ follow a joint bivariate normal distribution.

---

### Q4: In Problem 3, why did the high-variance dataset have a lower Pearson $r$ despite having the exact same true underlying slope?
**Answer:**
The generative model is $Y = \beta X + \alpha + \epsilon$ where $\epsilon \sim \mathcal{N}(0, \sigma_\epsilon^2)$.
Theoretical variance of $Y$ is:
$$\text{Var}(Y) = \beta^2 \text{Var}(X) + \sigma_\epsilon^2$$
Theoretical covariance is:
$$\text{Cov}(X, Y) = \text{Cov}(X, \beta X + \epsilon) = \beta \text{Var}(X)$$
Therefore, the theoretical correlation coefficient is:
$$r = \frac{\beta \text{Var}(X)}{\sqrt{\text{Var}(X)} \cdot \sqrt{\beta^2 \text{Var}(X) + \sigma_\epsilon^2}} = \frac{1}{\sqrt{1 + \frac{\sigma_\epsilon^2}{\beta^2 \text{Var}(X)}}}$$
As noise variance $\sigma_\epsilon^2$ increases, the denominator increases, monotonically driving $r$ toward $0$.

---

### Q5: What are the risks of using extreme train-test splits such as $10:90$ or $90:10$?
**Answer:**
- **$10:90$ Split ($10\%$ Train, $90\%$ Test):** High estimation variance in model parameters (under-fitting / parameter instability) because the model sees too few samples ($N_{\text{train}} = 3$), though test evaluation error has low variance.
- **$90:10$ Split ($90\%$ Train, $10\%$ Test):** The model learns robust parameters ($N_{\text{train}} = 27$), but the test set is too small ($N_{\text{test}} = 3$), leading to extreme volatility and wide confidence intervals on test performance metrics.
- **Standard Practice:** Balanced splits like $70:30$ or $80:20$ or $K$-fold cross-validation are preferred to optimize the bias-variance tradeoff.

---

## 6. Verification & Completion Checklist

- [x] Problem 1(a): Feature count (1), sample count (30), and salary range computed.
- [x] Problem 1(b): Scatter plot generated and verified.
- [x] Problem 1(c): Train-test splits from $10:90$ to $90:10$ logged.
- [x] Problem 1(d): Manual variance, standard deviation, and covariance evaluated.
- [x] Problem 1(e): Manual Pearson $r = 0.9782$ calculated without library shortcuts.
- [x] Problem 2: Positive ($r = +0.994$) and negative ($r = -0.993$) datasets generated and plotted.
- [x] Problem 3: High vs. low variance noise modeling analyzed.
- [x] Problem 4: Fertilizer vs. crop population ($N=20$) and sample ($n=9$) statistics evaluated.
- [x] All plots saved in `CS360/LAB2/plots/`.
- [x] Complete numerical output saved in `CS360/LAB2/outputs/experiment_results.txt`.
- [x] Strict KaTeX compliance with zero underscore or ampersand errors.


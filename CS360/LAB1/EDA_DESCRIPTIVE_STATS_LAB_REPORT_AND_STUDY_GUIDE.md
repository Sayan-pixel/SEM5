# CS360 Machine Learning Lab — Lab 1 Report & Master Study Guide
# Stochastic State Space Traversal, Markovian Jump Chains & Path Parity Analysis

**Course:** CS360: Machine Learning Laboratory (CS306)  
**Department:** Computer Science and Engineering  
**Institution:** Indian Institute of Information Technology Guwahati (IIITG)  
**Experiment:** Lab 1 — Discrete State Space Traversal, Empirical Monte Carlo Simulation, Path Parity Determinism, and Arbitrary-Precision Scalability  

---

## 1. Executive Summary & Problem Overview

In computational machine learning, stochastic processes, and reinforcement learning, understanding **state-space traversals** and **absorption times** in discrete Markov chains forms the theoretical bedrock for convergence analysis, exploration vs. exploitation bounds, and algorithmic scalability.

This laboratory experiment explores an absorbing Markovian jump process defined over non-negative integers $\mathbb{N}_0 = \{0, 1, 2, \dots\}$. The system obeys the following transition dynamics:
- The system starts at an initial state $n \in \mathbb{N}_0$.
- If the current state is $k > 0$, the next state $X_{\text{next}}$ is selected via a **discrete uniform distribution** over all preceding states:

$$X_{\text{next}} \sim \text{Uniform}(\{0, 1, 2, \dots, k - 1\})$$

- The transition probability between any state $k > 0$ and state $j < k$ is identically:

$$P(X_{t+1} = j \mid X_t = k) = \frac{1}{k}, \quad \forall j \in \{0, 1, \dots, k - 1\}$$

- State $0$ is an **absorbing sink state** ($P(0 \mid 0) = 1$). Upon reaching state $0$, the traversal terminates immediately.

```
State Transition Dynamics:
  State k -----> {0, 1, 2, ..., k-1} with probability 1/k each
  State 0 -----> (Absorbing Sink)
```

The experiment systematically progresses through three computational tiers:
1. **Level 1 (Trace Analysis):** Monte Carlo empirical simulation of the trajectory from $n = 50$ down to $0$ over $10^4$ trials, tracking empirical average path lengths and distribution profiles.
2. **Level 2 (Path Parity Determinism):** Closed-form deterministic calculation of the probability that the total jump path length is an **even number** for $n = 2000$ in $O(n^2)$ or better without simulation libraries.
3. **Level 3 (Computational Scalability):** Exact asymptotic calculation of the expected path length for an astronomical state $n = 10^{500}$ in $O(1)$ time complexity without recursion or iteration, circumventing standard IEEE 754 floating-point buffer overflow.

---

## 2. Mathematical Foundations & Theoretical Proofs

### 2.1 First-Step Analysis for Expected Path Length
Let $E_n = \mathbb{E}[L \mid X_0 = n]$ denote the expected number of steps (path length) required for the system to reach the absorbing sink state $0$ starting from state $n$.

By boundary condition, starting at the sink requires zero transitions:

$$E_0 = 0$$

For any non-zero state $n \ge 1$, applying the Law of Total Expectation via **First-Step Analysis**:

$$E_n = 1 + \sum_{k=0}^{n-1} P(X_1 = k \mid X_0 = n) \cdot E_k = 1 + \frac{1}{n} \sum_{k=0}^{n-1} E_k$$

Multiplying both sides by $n$:

$$n E_n = n + \sum_{k=0}^{n-1} E_k \quad \text{--- (Equation 1)}$$

Writing the corresponding equation for state $n - 1$ (for $n \ge 2$):

$$(n - 1) E_{n-1} = (n - 1) + \sum_{k=0}^{n-2} E_k \quad \text{--- (Equation 2)}$$

Subtracting Equation 2 from Equation 1 eliminates the summation:

$$n E_n - (n - 1) E_{n-1} = 1 + E_{n-1}$$

Rearranging the terms:

$$n E_n = n E_{n-1} + 1 \implies E_n = E_{n-1} + \frac{1}{n}$$

Unrolling this recurrence relation from $E_0 = 0$:

$$E_1 = E_0 + \frac{1}{1} = 1$$

$$E_2 = E_1 + \frac{1}{2} = 1 + \frac{1}{2}$$

$$E_n = \sum_{i=1}^n \frac{1}{i} = H_n$$

Where $H_n$ is the classical **$n$-th Harmonic Number**.

### 2.2 Proof of Logarithmic Asymptotic Growth
The Euler-Maclaurin summation formula provides the asymptotic expansion for Harmonic numbers:

$$H_n = \ln(n) + \gamma + \frac{1}{2n} - \frac{1}{12n^2} + O(n^{-4})$$

Where $\gamma \approx 0.57721566490153286...$ is the **Euler-Mascheroni constant**.

As $n \to \infty$:

$$\lim_{n \to \infty} \frac{E_n}{\ln(n)} = 1$$

Thus, the expected path length exhibits strictly **logarithmic growth**:

$$E_n \sim \Theta(\ln n)$$

```
Expected Path Length Recurrence:
  E_0 = 0
  E_1 = 1
  E_2 = 1 + 1/2 = 1.5
  E_3 = 1 + 1/2 + 1/3 = 1.833...
  ...
  E_n = H_n ~ ln(n) + gamma
```

---

### 2.3 Mathematical Derivation of Path Parity Determinism (Level 2)

Let $P_n$ be the probability that a path starting from state $n$ takes an **even number of steps** to reach state $0$.
Let $Q_n = 1 - P_n$ be the probability that it takes an **odd number of steps**.

#### Boundary Conditions:
- At state $0$: 0 steps are taken. Since 0 is an even integer:

$$P_0 = 1, \quad Q_0 = 0$$

- At state $1$: The only accessible next state is $0$. Exactly 1 jump is made (odd):

$$P_1 = 0, \quad Q_1 = 1$$

#### First-Step Recurrence for General $n \ge 1$:
If the first transition jumps to state $k \in \{0, 1, \dots, n - 1\}$, one step has been consumed. For the total path length to be even, the remaining path from state $k$ must have an **odd** length:

$$P_n = \frac{1}{n} \sum_{k=0}^{n-1} Q_k = \frac{1}{n} \sum_{k=0}^{n-1} (1 - P_k) = 1 - \frac{1}{n} \sum_{k=0}^{n-1} P_k$$

Multiplying by $n$:

$$n P_n = n - \sum_{k=0}^{n-1} P_k \quad \text{--- (Equation A)}$$

Similarly, for state $n - 1$:

$$(n - 1) P_{n-1} = (n - 1) - \sum_{k=0}^{n-2} P_k \quad \text{--- (Equation B)}$$

Subtracting Equation B from Equation A:

$$n P_n - (n - 1) P_{n-1} = 1 - P_{n-1}$$

Rearranging gives:

$$n P_n = 1 + (n - 2) P_{n-1} \implies P_n = \frac{1}{n} + \frac{n - 2}{n} P_{n-1}$$

#### Inductive Evaluation:
1. For $n = 2$:
   $$P_2 = \frac{1}{2} + \frac{2 - 2}{2} P_1 = \frac{1}{2} + 0 = \frac{1}{2}$$
2. For $n = 3$:
   $$P_3 = \frac{1}{3} + \frac{1}{3} P_2 = \frac{1}{3} + \frac{1}{3} \left(\frac{1}{2}\right) = \frac{1}{3} + \frac{1}{6} = \frac{3}{6} = \frac{1}{2}$$
3. For $n = 4$:
   $$P_4 = \frac{1}{4} + \frac{2}{4} P_3 = \frac{1}{4} + \frac{2}{4} \left(\frac{1}{2}\right) = \frac{1}{4} + \frac{1}{4} = \frac{1}{2}$$

#### Inductive Hypothesis:
Assume $P_{k} = \frac{1}{2}$ for all $k \ge 2$. Then for $k + 1$:

$$P_{k+1} = \frac{1}{k+1} + \frac{k - 1}{k + 1} \left(\frac{1}{2}\right) = \frac{2 + (k - 1)}{2(k + 1)} = \frac{k + 1}{2(k + 1)} = \frac{1}{2}$$

#### Fundamental Parity Invariant:
$$\boxed{P_n = \frac{1}{2}, \quad \forall n \ge 2}$$

For $n = 2000$, the exact probability of an even path length is identically:

$$P_{2000} = \frac{1}{2}$$

The dynamic programming recurrence computes this in $O(n)$ time using exact rational fractions (`fractions.Fraction`), satisfying all assignment constraints without simulation.

---

## 3. High-Performance Software Architecture

The implementation in `assignment1.py` and `run_experiments.py` cleanly separates empirical simulation from exact analytical solutions.

### 3.1 Level 1: Monte Carlo Simulation (`simulate_state_space_traversal`)
```python
def simulate_state_space_traversal(n, num_simulations=10000, seed=42):
    random.seed(seed)
    path_lengths = []
    for _ in range(num_simulations):
        current_state = n
        path_length = 0
        while current_state > 0:
            current_state = random.randint(0, current_state - 1)
            path_length += 1
        path_lengths.append(path_length)
        
    return sum(path_lengths) / num_simulations, path_lengths
```
- **Time Complexity:** Average trajectory takes $O(\ln n)$ transitions. For $M = 10^4$ trials, total complexity is $O(M \ln n) \approx 10^4 \times 4.5 = 45,000$ operations, executing in under $0.05$ seconds.
- **Space Complexity:** $O(M)$ to record lengths for histogram distribution plotting.

### 3.2 Level 2: Deterministic Parity Calculation (`exact_even_path_probability`)
```python
def exact_even_path_probability(n):
    if n == 0:
        return Fraction(1, 1)
    if n == 1:
        return Fraction(0, 1)
        
    p = Fraction(0, 1)
    for i in range(2, n + 1):
        p = Fraction(1, i) + Fraction(i - 2, i) * p
        
    return p
```
- **Time Complexity:** $O(n)$ iterations involving rational fraction additions.
- **Memory Complexity:** $O(1)$ auxiliary memory since only the preceding state $p$ is stored.

### 3.3 Level 3: Arbitrary-Precision Scalability (`compute_large_average_path_length`)
```python
def compute_large_average_path_length(n_str, precision=50):
    decimal.getcontext().prec = precision 
    
    # 50-digit Euler-Mascheroni constant
    gamma = decimal.Decimal('0.57721566490153286060651209008240243104215933593992')
    n_dec = decimal.Decimal(n_str)
    
    # Asymptotic approximation H_n = ln(n) + gamma
    expected_path_length = n_dec.ln() + gamma
    return expected_path_length
```

#### Why IEEE 754 Hardware Floats Fail:
1. Standard 64-bit IEEE 754 double precision floats have a 53-bit mantissa and an 11-bit exponent, allowing a maximum magnitude of $\approx 1.797693 \times 10^{308}$.
2. The initial state $n = 10^{500}$ exceeds the maximum floating-point exponent, causing an immediate hardware overflow (`OverflowError: int too large to convert to float`).
3. Even if $n$ could be represented, computing $H_n = \sum_{i=1}^{10^{500}} \frac{1}{i}$ via a loop would require $10^{500}$ operations. For comparison, the observable universe is approximately $4.3 \times 10^{17}$ seconds old; executing $10^{500}$ operations on any physical supercomputer is computationally impossible.
4. Using $H_n \approx \ln(n) + \gamma$ with Python's arbitrary-precision `decimal` library evaluates $\ln(10^{500}) = 500 \cdot \ln(10)$ in $O(1)$ time, yielding $50$ digits of precision with zero buffer overflow.

---

## 4. Experimental Results & Verification

All experimental artifacts are organized into structured directories:
- **Plots Directory:** `CS360/LAB1/plots/`
- **Outputs Directory:** `CS360/LAB1/outputs/`

### 4.1 Numerical Log Summary (`outputs/experiment_results.txt`)
```text
CS 360 / CS 306: Machine Learning Lab - Assignment 1 Results Log
=================================================================

--- Level 1: Trace Analysis ---
Initial State n: 50
Number of Simulations: 10,000
Empirical Mean Path Length: 4.492900
Theoretical Harmonic Mean H_50: 4.499205
Absolute Simulation Error: 0.006305

--- Level 2: Path Parity Determinism ---
Initial State n: 2000
Exact Probability of Even Path Length (Fraction): 1/2
Float Equivalent: 0.500000
Proof invariant: For all n >= 2, P(even) = 1/2 identically.

--- Level 3: Computational Scalability ---
Initial State n: 10^500 (501 decimal digits)
Precision: 50 decimal places
Expected Path Length: 1151.8697621619243748696022394322645062315929036503
Analytical Verification: 500 * ln(10) + gamma = 1151.8697621619...
```

### 4.2 Visual Verification

#### Figure 1: Path Length Empirical Distribution ($n = 50$)
The empirical distribution shows positive skewness characteristic of Poisson-like jump processes, with the empirical mean ($4.4929$) aligning closely with theoretical $H_{50} = 4.4992$.
*Generated at:* `CS360/LAB1/plots/path_length_distribution_n50.png`

#### Figure 2: Scaling of Expected Path Length ($E_n$ vs. $n$)
Validates the convergence of Monte Carlo simulation points to the exact harmonic sum $H_n$ and its asymptotic logarithmic envelope $\ln(n) + \gamma$.
*Generated at:* `CS360/LAB1/plots/expected_path_length_vs_n.png`

---

## 5. Comprehensive Viva-Voce Questions & In-Depth Solutions

### Q1: What is a Markov chain, and does the state-space traversal in this assignment satisfy the Markov property?
**Answer:**
A stochastic process possesses the **Markov Property** (memorylessness) if the conditional probability distribution of future states depends solely on the current state, not on the sequence of preceding states:

$$P(X_{t+1} = j \mid X_t = k, X_{t-1} = s_{t-1}, \dots, X_0 = s_0) = P(X_{t+1} = j \mid X_t = k)$$

The state-space traversal in this assignment strictly satisfies the Markov property: at any state $k > 0$, the router or system selects its next state uniformly at random from $\{0, 1, \dots, k - 1\}$ with probability $1/k$, irrespective of which states it visited before reaching $k$.

---

### Q2: Why is the expected number of jumps to reach state $0$ from state $n$ exactly the $n$-th Harmonic number $H_n$?
**Answer:**
From First-Step Analysis, the recurrence for the expected path length is:

$$E_n = 1 + \frac{1}{n} \sum_{k=0}^{n-1} E_k$$

Subtracting $(n-1)E_{n-1} = (n-1) + \sum_{k=0}^{n-2} E_k$ yields the difference equation:

$$n E_n - (n - 1) E_{n-1} = 1 + E_{n-1} \implies E_n = E_{n-1} + \frac{1}{n}$$

Since $E_0 = 0$, unrolling this telescopic sum from $1$ to $n$ yields:

$$E_n = \sum_{i=1}^n \frac{1}{i} = H_n$$

---

### Q3: Why does the probability of an even path length equal exactly $0.5$ for every $n \ge 2$?
**Answer:**
Let $P_n$ be the probability of an even path length from state $n$. By first-step analysis:

$$P_n = \frac{1}{n} + \frac{n - 2}{n} P_{n-1}$$

For $n = 2$: $P_2 = \frac{1}{2} + 0 \cdot P_1 = \frac{1}{2}$.
If $P_{n-1} = \frac{1}{2}$, substituting into the recurrence gives:

$$P_n = \frac{1}{n} + \frac{n - 2}{n} \left(\frac{1}{2}\right) = \frac{2 + (n - 2)}{2n} = \frac{n}{2n} = \frac{1}{2}$$

By mathematical induction, $P_n = \frac{1}{2}$ holds identically for all $n \ge 2$. At each step above $1$, the symmetric structure of uniform transitions balances odd and even remaining paths.

---

### Q4: Why can't we compute the Harmonic sum for $n = 10^{500}$ using a loop in Python?
**Answer:**
A standard modern processor executes roughly $10^9$ to $10^{10}$ clock cycles per second. A loop executing $10^{500}$ iterations would require approximately $10^{491}$ seconds—vastly exceeding the age of the universe ($\approx 4.3 \times 10^{17}$ seconds). Computing it iteratively is physically impossible. Furthermore, an IEEE 754 64-bit float overflows at $\approx 1.8 \times 10^{308}$. We must use the analytical asymptotic form $H_n \approx \ln(n) + \gamma$ evaluated with arbitrary-precision arithmetic (`decimal` module), which executes in $O(1)$ time.

---

### Q5: What is the variance of the path length from state $n$ to state $0$?
**Answer:**
Let $L_n$ be the random variable denoting the path length from state $n$. Each step from state $k$ can be represented as an independent geometric-like indicator. The variance satisfies:

$$\text{Var}(L_n) = \sum_{i=1}^n \left(\frac{1}{i} - \frac{1}{i^2}\right) = H_n - H_n^{(2)}$$

Where $H_n^{(2)} = \sum_{i=1}^n \frac{1}{i^2}$. As $n \to \infty$, $H_n^{(2)} \to \frac{\pi^2}{6} \approx 1.64493$.
Therefore:

$$\text{Var}(L_n) \approx \ln(n) + \gamma - \frac{\pi^2}{6}$$

The variance also grows logarithmically with $n$.

---

### Q6: How is this problem connected to randomized algorithms, such as Randomized QuickSort?
**Answer:**
In Randomized QuickSort, when sorting an array of size $n$, a pivot is chosen uniformly at random from the remaining elements, partitioning the problem into subproblems of random sizes. The recurrence for the depth of recursion and comparison counts mirrors the Harmonic progression $\Theta(n \ln n)$, derived from the same underlying discrete uniform jump process over permutations and order statistics.

---

## 6. Verification & Completion Checklist

- [x] Level 1: Trace analysis implemented with random seed handling and verified against $H_{50}$.
- [x] Level 2: Exact path parity recurrence implemented without simulation or external libraries.
- [x] Level 3: Arbitrary-precision logarithmic scalability calculated for $n = 10^{500}$ in $O(1)$ time.
- [x] Empirical plots generated in `CS360/LAB1/plots/`.
- [x] Execution logs saved in `CS360/LAB1/outputs/`.
- [x] Strict adherence to GitHub KaTeX guidelines (no unescaped underscores, ampersands, or broken math tokens).


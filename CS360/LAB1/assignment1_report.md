# CS 306: Machine Learning Lab - Assignment 1
## Technical Requirements Report

### 1. Python Source Code
The Python source code for all three levels is provided in `assignment1.py`.

### 2. Proof of Logarithmic Growth in Path Length

Let $E_n$ be the expected path length from state $n$. By definition, the system terminates at state 0, so $E_0 = 0$.

For any state $n > 0$, the next state $k$ is chosen from a uniform discrete distribution over the set $\{0, 1, \dots, n-1\}$. The probability of transitioning to any specific state $k$ in this set is $\frac{1}{n}$.

The expected path length from state $n$ is 1 (for the transition itself) plus the average of the expected path lengths from all possible next states $k$:

$$E_n = 1 + \frac{1}{n} \sum_{k=0}^{n-1} E_k$$

Multiply both sides by $n$:
$$n E_n = n + \sum_{k=0}^{n-1} E_k \quad \text{--- (Equation 1)}$$

Similarly, for the state $n-1$:
$$(n-1) E_{n-1} = (n-1) + \sum_{k=0}^{n-2} E_k \quad \text{--- (Equation 2)}$$

Subtracting Equation 2 from Equation 1 gives:
$$n E_n - (n-1) E_{n-1} = 1 + E_{n-1}$$
$$n E_n = 1 + n E_{n-1}$$
$$E_n = E_{n-1} + \frac{1}{n}$$

By unrolling this recurrence relation down to $E_0 = 0$, we find that:
$$E_n = \sum_{i=1}^n \frac{1}{i}$$

This is the definition of the $n$-th Harmonic number, denoted as $H_n$. 
The asymptotic expansion for the Harmonic number is well known:
$$H_n \approx \ln(n) + \gamma + \frac{1}{2n} - O(n^{-2})$$

where $\gamma \approx 0.57721$ is the Euler-Mascheroni constant. 
As $n \to \infty$, the dominant term is $\ln(n)$. Therefore, $E_n \sim \ln(n)$, proving that the state-transition logic leads to logarithmic growth in path length.

### 3. Handling Precision Requirements for $n = 10^{500}$

A standard IEEE 754 64-bit floating-point number (used by Python's `float` type) has a maximum representable value of approximately $1.79 \times 10^{308}$. Attempting to cast $n=10^{500}$ directly to a standard `float` will immediately cause an `OverflowError` in Python. 

To handle this without buffer overflow or precision loss, the solution utilizes Python's `decimal` module, which supports arbitrary-precision arithmetic. 

Furthermore, instead of attempting to compute the exact Harmonic number using iterations (which is impossible for $10^{500}$ operations due to time limits), we utilize the asymptotic approximation $H_n \approx \ln(n) + \gamma$. 
For $n = 10^{500}$, the error term $\frac{1}{2n}$ and subsequent terms are astronomically small ($\sim 10^{-500}$) and fall far beyond standard precision needs (we can safely limit our `decimal` context precision to 50 decimal places). 

By evaluating `decimal.Decimal(n_str).ln() + gamma`, we securely calculate the expected path length in $O(1)$ time within standard memory limits, avoiding any hardware float limitations entirely.

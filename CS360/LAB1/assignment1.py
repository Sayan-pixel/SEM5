import os
import random
import decimal
from fractions import Fraction
import matplotlib.pyplot as plt
import numpy as np

# Set MPLCONFIGDIR to temp directory for writable matplotlib cache
os.environ["MPLCONFIGDIR"] = os.path.join(os.environ.get("TEMP", "C:/Temp"), "mpl_cache")

# ==========================================
# Level 1: Trace Analysis
# ==========================================
def simulate_state_space_traversal(n, num_simulations=10000, seed=42):
    """Simulate path from state n down to sink state 0 using uniform transitions."""
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

# ==========================================
# Level 2: Path Parity Determinism
# ==========================================
def exact_even_path_probability(n):
    """Compute exact rational probability that total path length is even."""
    if n == 0:
        return Fraction(1, 1)
    if n == 1:
        return Fraction(0, 1)
        
    p = Fraction(0, 1)
    for i in range(2, n + 1):
        # P_n = (1/n) + ((n-2)/n) * P_{n-1}
        p = Fraction(1, i) + Fraction(i - 2, i) * p
        
    return p

# ==========================================
# Level 3: Computational Scalability
# ==========================================
def compute_large_average_path_length(n_str, precision=50):
    """Compute expected path length for astronomical n in O(1) time without float overflow."""
    decimal.getcontext().prec = precision 
    
    # 50-digit Euler-Mascheroni constant (gamma)
    gamma = decimal.Decimal('0.57721566490153286060651209008240243104215933593992')
    n_dec = decimal.Decimal(n_str)
    expected_path_length = n_dec.ln() + gamma
    return expected_path_length

def run_experiments_and_generate_artifacts():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    plots_dir = os.path.join(base_dir, "plots")
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    # 1. Level 1 execution
    print("Level 1: Trace Analysis")
    mean_length, path_lengths = simulate_state_space_traversal(50, 10000)
    h_50 = sum(1.0 / i for i in range(1, 51))
    print(f"  Mean path length for n=50 over 10^4 simulations: {mean_length:.6f}")
    print(f"  Theoretical Harmonic Mean H_50: {h_50:.6f}")

    # Plot 1: Path length distribution for n=50
    plt.figure(figsize=(8, 5))
    plt.hist(path_lengths, bins=range(1, max(path_lengths) + 2), 
             density=True, alpha=0.75, color='#2b5c8f', edgecolor='black')
    plt.axvline(mean_length, color='#d9534f', linestyle='dashed', linewidth=2, 
                label=f'Empirical Mean = {mean_length:.4f}')
    plt.axvline(h_50, color='#5cb85c', linestyle='dotted', linewidth=2, 
                label=f'Theoretical $H_{{50}}$ = {h_50:.4f}')
    plt.title('Path Length Distribution from State $n=50$ to Sink State $0$ ($10^4$ Trials)')
    plt.xlabel('Path Length (Number of Transitions)')
    plt.ylabel('Empirical Probability Density')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "path_length_distribution_n50.png"), dpi=300)
    plt.close()

    # Plot 2: Empirical Mean vs Theoretical Harmonic Number across multiple n
    n_values = [1, 2, 5, 10, 20, 30, 40, 50, 75, 100]
    sim_means = []
    theory_means = []
    for nv in n_values:
        sm, _ = simulate_state_space_traversal(nv, 2000)
        sim_means.append(sm)
        theory_means.append(sum(1.0 / i for i in range(1, nv + 1)))

    plt.figure(figsize=(8, 5))
    plt.plot(n_values, sim_means, 'o-', color='#d9534f', label='Simulation ($10^3$ runs)')
    plt.plot(n_values, theory_means, 's--', color='#2b5c8f', label='Theoretical $H_n = \sum 1/i$')
    plt.plot(n_values, [np.log(nv) + 0.57721566 for nv in n_values], ':', color='#f0ad4e', label='Asymptotic $\ln(n) + \gamma$')
    plt.title('Expected Path Length $E_n$ vs Initial State $n$')
    plt.xlabel('Initial State $n$')
    plt.ylabel('Expected Path Length (Transitions)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "expected_path_length_vs_n.png"), dpi=300)
    plt.close()

    # 2. Level 2 execution
    print("\nLevel 2: Path Parity Determinism")
    prob_even_2000 = exact_even_path_probability(2000)
    print(f"  Exact probability of even path length for n=2000: {prob_even_2000}")
    print(f"  Float Equivalent: {float(prob_even_2000)}")

    # 3. Level 3 execution
    print("\nLevel 3: Computational Scalability")
    n_large_str = "1" + "0" * 500
    avg_len_large = compute_large_average_path_length(n_large_str)
    print(f"  Average path length for n=10^500: {avg_len_large}")

    # Save detailed output report
    output_log_path = os.path.join(outputs_dir, "experiment_results.txt")
    with open(output_log_path, "w", encoding="utf-8") as f:
        f.write("CS 360 / CS 306: Machine Learning Lab - Assignment 1 Results Log\n")
        f.write("="*65 + "\n\n")
        f.write("--- Level 1: Trace Analysis ---\n")
        f.write(f"Initial State n: 50\n")
        f.write(f"Number of Simulations: 10,000\n")
        f.write(f"Empirical Mean Path Length: {mean_length:.6f}\n")
        f.write(f"Theoretical Harmonic Mean H_50: {h_50:.6f}\n")
        f.write(f"Absolute Simulation Error: {abs(mean_length - h_50):.6f}\n\n")
        
        f.write("--- Level 2: Path Parity Determinism ---\n")
        f.write(f"Initial State n: 2000\n")
        f.write(f"Exact Probability of Even Path Length (Fraction): {prob_even_2000}\n")
        f.write(f"Float Equivalent: {float(prob_even_2000):.6f}\n")
        f.write("Proof invariant: For all n >= 2, P(even) = 1/2 identically.\n\n")

        f.write("--- Level 3: Computational Scalability ---\n")
        f.write(f"Initial State n: 10^500 (501 decimal digits)\n")
        f.write(f"Precision: 50 decimal places\n")
        f.write(f"Expected Path Length: {avg_len_large}\n")
        f.write(f"Analytical Verification: 500 * ln(10) + gamma = 1151.8697621619...\n")

    print("\nArtifacts and logs saved in 'plots/' and 'outputs/'.")

if __name__ == "__main__":
    run_experiments_and_generate_artifacts()

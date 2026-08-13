import random
import decimal
from fractions import Fraction

# ==========================================
# Level 1: Trace Analysis
# ==========================================
def simulate_state_space_traversal(n, num_simulations=10000):

    random.seed(42)
    
    total_length = 0
    for _ in range(num_simulations):
        current_state = n
        path_length = 0
        while current_state > 0:
            current_state = random.randint(0, current_state - 1)
            path_length += 1
        total_length += path_length
        
    return total_length / num_simulations

# ==========================================
# Level 2: Path Parity Determinism
# ==========================================
def exact_even_path_probability(n):
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
def compute_large_average_path_length(n_str):
    decimal.getcontext().prec = 50 
    
    # Euler-Mascheroni constant
    gamma = decimal.Decimal('0.57721566490153286060651209008240243104215933593992')
    
    n_dec = decimal.Decimal(n_str)
    
    expected_path_length = n_dec.ln() + gamma
    
    return expected_path_length

if __name__ == "__main__":
    # Level 1 test
    print("Level 1:")
    mean_length = simulate_state_space_traversal(50, 10**4)
    print(f"Mean path length for n=50 over 10^4 simulations: {mean_length}")
    
    # Level 2 test
    print("\nLevel 2:")
    prob_even = exact_even_path_probability(2000)
    print(f"Exact probability of even path length for n=2000: {prob_even}")
    
    # Level 3 test
    print("\nLevel 3:")
    n_val = "1" + "0" * 500  # 10^500
    avg_len_large = compute_large_average_path_length(n_val)
    print(f"Average path length for n=10^500: {avg_len_large}")

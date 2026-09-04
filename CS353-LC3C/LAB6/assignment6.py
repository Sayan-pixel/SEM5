import numpy as np
import matplotlib.pyplot as plt

# Setup
np.random.seed(42)
H = 10000
G_vals = np.linspace(0.1, 3.0, 30)

def simulate_pure_aloha(G):
    # N ~ Poisson(G * H)
    N = np.random.poisson(G * H)
    arrivals = np.sort(np.random.uniform(0, H, N))
    
    successes = 0
    for i in range(N):
        prev_t = arrivals[i-1] if i > 0 else -float('inf')
        next_t = arrivals[i+1] if i < N-1 else float('inf')
        
        # Successful if no other frame starts within 1 frame-time
        if (arrivals[i] - prev_t > 1) and (next_t - arrivals[i] > 1):
            successes += 1
            
    return successes / H

def simulate_slotted_aloha(G):
    successes = 0
    for slot in range(H):
        k = np.random.poisson(G)
        if k == 1:
            successes += 1
    return successes / H

def simulate_csma(G, a):
    N = np.random.poisson(G * H)
    arrivals = np.sort(np.random.uniform(0, H, N))
    
    successes = 0
    idx = 0
    T_idle = 0
    deferred_count = 0
    
    while idx < N or deferred_count > 0:
        if deferred_count == 0:
            if idx >= N:
                break
            # Channel idle, next arrival starts
            t_start = arrivals[idx]
            idx += 1
            
            transmitting_count = 1
            last_transmit_time = t_start
            
            # Others arriving within vulnerable window 'a' also sense idle and transmit
            while idx < N and arrivals[idx] <= t_start + a:
                transmitting_count += 1
                last_transmit_time = arrivals[idx]
                idx += 1
                
            if transmitting_count == 1:
                successes += 1
                
            T_idle = last_transmit_time + 1 + a
            
            # Count deferred arrivals during the busy period
            deferred_count = 0
            while idx < N and arrivals[idx] <= T_idle:
                deferred_count += 1
                idx += 1
                
        else:
            # Deferred arrivals transmit as soon as channel is idle
            t_start = T_idle
            transmitting_count = deferred_count
            
            last_transmit_time = t_start
            # New arrivals in the vulnerable window
            while idx < N and arrivals[idx] <= t_start + a:
                transmitting_count += 1
                last_transmit_time = arrivals[idx]
                idx += 1
                
            if transmitting_count == 1:
                successes += 1
                
            T_idle = last_transmit_time + 1 + a
            
            # Count newly deferred arrivals
            deferred_count = 0
            while idx < N and arrivals[idx] <= T_idle:
                deferred_count += 1
                idx += 1
                
    return successes / H

def run_simulation():
    S_pure = []
    S_slotted = []
    S_csma = []
    S_csma_05 = []
    S_csma_10 = []
    
    print("Simulating protocols...")
    
    for G in G_vals:
        S_pure.append(simulate_pure_aloha(G))
        S_slotted.append(simulate_slotted_aloha(G))
        S_csma.append(simulate_csma(G, 0.01))
        S_csma_05.append(simulate_csma(G, 0.05))
        S_csma_10.append(simulate_csma(G, 0.1))
        
    S_pure = np.array(S_pure)
    S_slotted = np.array(S_slotted)
    S_csma = np.array(S_csma)
    S_csma_05 = np.array(S_csma_05)
    S_csma_10 = np.array(S_csma_10)

    # Analytical curves
    pure_analytical = G_vals * np.exp(-2 * G_vals)
    slotted_analytical = G_vals * np.exp(-G_vals)

    # Find peaks
    peak_pure_idx = np.argmax(S_pure)
    peak_slotted_idx = np.argmax(S_slotted)
    peak_csma_idx = np.argmax(S_csma)
    peak_csma_05_idx = np.argmax(S_csma_05)
    peak_csma_10_idx = np.argmax(S_csma_10)
    
    print(f"Pure Aloha Peak S = {S_pure[peak_pure_idx]:.4f} at G = {G_vals[peak_pure_idx]:.2f}")
    print(f"Slotted Aloha Peak S = {S_slotted[peak_slotted_idx]:.4f} at G = {G_vals[peak_slotted_idx]:.2f}")
    print(f"CSMA (a=0.01) Peak S = {S_csma[peak_csma_idx]:.4f} at G = {G_vals[peak_csma_idx]:.2f}")
    print(f"CSMA (a=0.05) Peak S = {S_csma_05[peak_csma_05_idx]:.4f} at G = {G_vals[peak_csma_05_idx]:.2f}")
    print(f"CSMA (a=0.10) Peak S = {S_csma_10[peak_csma_10_idx]:.4f} at G = {G_vals[peak_csma_10_idx]:.2f}")

    # Plot 1: Pure Aloha vs Analytical
    plt.figure(figsize=(10, 6))
    plt.plot(G_vals, S_pure, label='Simulated Pure Aloha', marker='o')
    plt.plot(G_vals, pure_analytical, label='Analytical Pure Aloha', linestyle='--')
    plt.xlabel('Offered Load (G)')
    plt.ylabel('Throughput (S)')
    plt.title('Pure Aloha: Simulated vs Analytical')
    plt.legend()
    plt.grid(True)
    plt.savefig('pure_aloha.png')
    
    # Plot 2: Slotted Aloha vs Analytical
    plt.figure(figsize=(10, 6))
    plt.plot(G_vals, S_slotted, label='Simulated Slotted Aloha', marker='o')
    plt.plot(G_vals, slotted_analytical, label='Analytical Slotted Aloha', linestyle='--')
    plt.xlabel('Offered Load (G)')
    plt.ylabel('Throughput (S)')
    plt.title('Slotted Aloha: Simulated vs Analytical')
    plt.legend()
    plt.grid(True)
    plt.savefig('slotted_aloha.png')
    
    # Plot 3: All three protocols (Part D)
    plt.figure(figsize=(10, 6))
    plt.plot(G_vals, S_pure, label='Pure Aloha')
    plt.plot(G_vals, S_slotted, label='Slotted Aloha')
    plt.plot(G_vals, S_csma, label='1-persistent CSMA (a=0.01)')
    plt.xlabel('Offered Load (G)')
    plt.ylabel('Throughput (S)')
    plt.title('Comparison of MAC Protocols')
    plt.legend()
    plt.grid(True)
    plt.savefig('comparison.png')

    # Plot 4: CSMA with different 'a' values
    plt.figure(figsize=(10, 6))
    plt.plot(G_vals, S_csma, label='CSMA (a=0.01)')
    plt.plot(G_vals, S_csma_05, label='CSMA (a=0.05)')
    plt.plot(G_vals, S_csma_10, label='CSMA (a=0.10)')
    plt.xlabel('Offered Load (G)')
    plt.ylabel('Throughput (S)')
    plt.title('CSMA with Varying Propagation Delay (a)')
    plt.legend()
    plt.grid(True)
    plt.savefig('csma_varying_a.png')
    
    print("Plots saved successfully.")

if __name__ == "__main__":
    run_simulation()

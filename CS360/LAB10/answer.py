import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram # Only used for plotting the dendrogram visually

# ==========================================
# 1(a). Read and Prepare the Dataset
# ==========================================
FILEPATH = r"E:\IIIT G\SEM_5\CS360\LAB10\Mall_Customers.csv"
def load_data(filepath=FILEPATH):
    """
    Reads the Mall Customer dataset.
    Uses 'Annual Income (k$)' and 'Spending Score (1-100)' for 2D clustering.
    """
    try:
        df = pd.read_csv(filepath)
        # Using columns 3 and 4 (Annual Income and Spending Score)
        X = df.iloc[:, [3, 4]].values 
        return X, df
    except FileNotFoundError:
        print("Dataset not found. Please ensure 'Mall_Customers.csv' is in the directory.")
        # Returning dummy data mimicking the distribution for execution safety
        np.random.seed(42)
        return np.random.rand(200, 2) * 100, None

# ==========================================
# 1(b). DBSCAN Implementation From Scratch
# ==========================================
def euclidean_distance(p1, p2):
    return np.sqrt(np.sum((p1 - p2)**2))

def region_query(X, point_idx, eps):
    neighbors = []
    for i in range(len(X)):
        if euclidean_distance(X[point_idx], X[i]) <= eps:
            neighbors.append(i)
    return neighbors

def dbscan_scratch(X, eps, minpts):
    labels = np.full(len(X), 0) # 0 = unassigned, -1 = noise, >0 = cluster
    cluster_id = 0
    
    for i in range(len(X)):
        if labels[i] != 0:
            continue
            
        neighbors = region_query(X, i, eps)
        
        if len(neighbors) < minpts:
            labels[i] = -1 # Mark as noise
        else:
            cluster_id += 1
            labels[i] = cluster_id
            
            # Expand cluster
            queue = [n for n in neighbors if n != i]
            while queue:
                q_point = queue.pop(0)
                if labels[q_point] == -1:
                    labels[q_point] = cluster_id # Change noise to border point
                if labels[q_point] == 0:
                    labels[q_point] = cluster_id
                    q_neighbors = region_query(X, q_point, eps)
                    if len(q_neighbors) >= minpts:
                        queue.extend(q_neighbors)
                        
    return labels

def silhouette_score_scratch(X, labels):
    """Simple internal metric to evaluate grid search without sklearn"""
    unique_labels = np.unique(labels)
    if len(unique_labels) <= 1 or (len(unique_labels) == 2 and -1 in unique_labels):
        return -1 # Invalid clustering

    s_scores = []
    for i in range(len(X)):
        if labels[i] == -1: 
            continue
            
        same_cluster = X[labels == labels[i]]
        if len(same_cluster) > 1:
            a_i = np.mean([euclidean_distance(X[i], p) for p in same_cluster if not np.array_equal(X[i], p)])
        else:
            a_i = 0
            
        b_i = float('inf')
        for cluster_label in unique_labels:
            if cluster_label == labels[i] or cluster_label == -1:
                continue
            other_cluster = X[labels == cluster_label]
            dist_to_other = np.mean([euclidean_distance(X[i], p) for p in other_cluster])
            if dist_to_other < b_i:
                b_i = dist_to_other
                
        s_i = (b_i - a_i) / max(a_i, b_i) if max(a_i, b_i) > 0 else 0
        s_scores.append(s_i)
        
    return np.mean(s_scores) if s_scores else -1

def dbscan_grid_search(X):
    minpts_values = range(4, 11)
    epsilon_values = [2, 2.5, 3, 3.5, 4]
    
    best_score = -1
    best_params = {'eps': None, 'minpts': None}
    best_labels = None
    
    print("Running Grid Search for DBSCAN...")
    for eps in epsilon_values:
        for minpts in minpts_values:
            labels = dbscan_scratch(X, eps, minpts)
            score = silhouette_score_scratch(X, labels)
            
            if score > best_score:
                best_score = score
                best_params = {'eps': eps, 'minpts': minpts}
                best_labels = labels.copy()
                
    print(f"Optimal Hyper-parameters from Grid Search: eps={best_params['eps']}, minpts={best_params['minpts']} (Score: {best_score:.3f})")
    return best_params, best_labels

# ==========================================
# 1(c). K-Distance Graph for Optimal Epsilon
# ==========================================
def k_distance_graph(X, k):
    distances = []
    for i in range(len(X)):
        dists = [euclidean_distance(X[i], X[j]) for j in range(len(X)) if i != j]
        dists.sort()
        distances.append(dists[k-1])  # k-th nearest neighbor
        
    distances.sort(reverse=True)
    
    # Coordinates of the start and end of the curve
    p1 = np.array([0, distances[0]])
    p2 = np.array([len(distances) - 1, distances[-1]])
    
    u = p2 - p1
    u_norm = np.linalg.norm(u)
    
    max_dist = 0
    optimal_eps = distances[0]
    optimal_idx = 0
    
    # Calculate distance from each point to the line connecting p1 and p2
    for i, d in enumerate(distances):
        p3 = np.array([i, d])
        v = p3 - p1
        
        # 2D cross product: u_x * v_y - u_y * v_x (compatible with NumPy 2.0+)
        cross_2d = u[0] * v[1] - u[1] * v[0]
        dist_to_line = np.abs(cross_2d) / u_norm
        
        if dist_to_line > max_dist:
            max_dist = dist_to_line
            optimal_eps = d
            optimal_idx = i
            
    # Plotting
    plt.figure(figsize=(8, 4))
    plt.plot(distances, label='K-Distance Curve')
    plt.axhline(y=optimal_eps, color='r', linestyle='--', label=f'Optimal Eps (Elbow) = {optimal_eps:.2f}')
    plt.plot(optimal_idx, optimal_eps, 'ro')
    plt.title(f'K-Distance Graph (k={k})')
    plt.xlabel('Points sorted by distance')
    plt.ylabel(f'{k}-th Nearest Neighbor Distance')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    return optimal_eps

# ==========================================
# 2(a). Hierarchical Clustering From Scratch
# ==========================================
def hierarchical_clustering_scratch(X, linkage='single'):
    n = len(X)
    # Z matrix for dendrogram: [cluster1, cluster2, distance, new_cluster_size]
    Z = np.zeros((n - 1, 4)) 
    
    # Initialize clusters and distances
    clusters = {i: [i] for i in range(n)}
    centroids = {i: X[i] for i in range(n)}
    
    # Initial distance matrix
    dist_matrix = np.full((n, n), np.inf)
    for i in range(n):
        for j in range(i + 1, n):
            dist_matrix[i, j] = euclidean_distance(X[i], X[j])
            dist_matrix[j, i] = dist_matrix[i, j]
            
    next_cluster_id = n
    active_clusters = list(range(n))
    
    for step in range(n - 1):
        # Find closest pair
        min_dist = np.inf
        c1, c2 = -1, -1
        
        for i in range(len(active_clusters)):
            for j in range(i + 1, len(active_clusters)):
                idx1 = active_clusters[i]
                idx2 = active_clusters[j]
                if dist_matrix[idx1, idx2] < min_dist:
                    min_dist = dist_matrix[idx1, idx2]
                    c1, c2 = idx1, idx2
                    
        # Merge c1 and c2
        new_cluster = clusters[c1] + clusters[c2]
        clusters[next_cluster_id] = new_cluster
        
        # Calculate new centroid
        size1, size2 = len(clusters[c1]), len(clusters[c2])
        centroids[next_cluster_id] = (size1 * centroids[c1] + size2 * centroids[c2]) / (size1 + size2)
        
        # Record merge in Z matrix format
        Z[step] = [c1, c2, min_dist, size1 + size2]
        
        # Update distances for the new cluster
        active_clusters.remove(c1)
        active_clusters.remove(c2)
        
        # Expand dist_matrix dynamically by appending rows/columns
        new_row_col = np.full((dist_matrix.shape[0] + 1, dist_matrix.shape[1] + 1), np.inf)
        new_row_col[:-1, :-1] = dist_matrix
        dist_matrix = new_row_col
        
        for ac in active_clusters:
            if linkage == 'single':
                d = min(dist_matrix[c1, ac], dist_matrix[c2, ac])
            elif linkage == 'complete':
                d = max(dist_matrix[c1, ac], dist_matrix[c2, ac])
            elif linkage == 'centroid':
                d = euclidean_distance(centroids[next_cluster_id], centroids[ac])
                
            dist_matrix[next_cluster_id, ac] = d
            dist_matrix[ac, next_cluster_id] = d
            
        active_clusters.append(next_cluster_id)
        next_cluster_id += 1
        
    return Z

# ==========================================
# Main Execution and Visualization
# ==========================================
def main():
    X, _ = load_data()
    
    # ---- TASK 1: DBSCAN ----
    # 1(b) Grid Search
    best_params, labels_grid = dbscan_grid_search(X)
    
    # 1(c) K-Distance Graph
    opt_k = best_params['minpts']
    print(f"\nGenerating K-Distance Graph for optimal minpts = {opt_k}...")
    opt_eps_kdist = k_distance_graph(X, opt_k)
    print(f"Optimal Epsilon from K-Distance Graph: {opt_eps_kdist:.2f}")
    
    labels_kdist = dbscan_scratch(X, opt_eps_kdist, opt_k)
    
    # Visualize 1(b) and 1(c)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    axes[0].scatter(X[:, 0], X[:, 1], c=labels_grid, cmap='viridis', s=50)
    axes[0].set_title(f"1(b) Grid Search DBSCAN (eps={best_params['eps']}, minpts={best_params['minpts']})")
    axes[0].set_xlabel('Annual Income (k$)')
    axes[0].set_ylabel('Spending Score (1-100)')
    
    axes[1].scatter(X[:, 0], X[:, 1], c=labels_kdist, cmap='viridis', s=50)
    axes[1].set_title(f"1(c) K-Distance DBSCAN (eps={opt_eps_kdist:.2f}, minpts={opt_k})")
    axes[1].set_xlabel('Annual Income (k$)')
    axes[1].set_ylabel('Spending Score (1-100)')
    plt.tight_layout()
    plt.show()
    
    # ---- TASK 2: Hierarchical Clustering ----
    print("\nRunning Hierarchical Clustering algorithms from scratch...")
    
    linkages = ['single', 'complete', 'centroid']
    Z_matrices = {}
    
    for link in linkages:
        Z_matrices[link] = hierarchical_clustering_scratch(X, linkage=link)
        
    # Visualize Dendrograms
    fig, axes = plt.subplots(3, 1, figsize=(12, 15))
    for i, link in enumerate(linkages):
        dendrogram(Z_matrices[link], ax=axes[i], truncate_mode='lastp', p=30)
        axes[i].set_title(f"Dendrogram - {link.capitalize()} Linkage")
        axes[i].set_xlabel("Cluster Size / Node Index")
        axes[i].set_ylabel("Distance")
        
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
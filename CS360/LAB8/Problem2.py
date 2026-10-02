import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Set seed for reproducibility
np.random.seed(42)

def k_means(X, K, max_iters=1000):
    n_samples, n_features = X.shape
    
    # Initialize centroids by randomly selecting K data points
    random_indices = np.random.choice(n_samples, K, replace=False)
    centroids = X[random_indices]
    
    cluster_assignments = np.zeros(n_samples)
    
    for epoch in range(max_iters):
        # Assignment Step: Calculate Euclidean distances from each point to each centroid
        distances = np.linalg.norm(X[:, np.newaxis, :] - centroids[np.newaxis, :, :], axis=2)
        new_cluster_assignments = np.argmin(distances, axis=1)
        
        # Stopping criteria: No changes in cluster assignment
        if np.array_equal(cluster_assignments, new_cluster_assignments):
            print(f"K={K} converged at epoch {epoch}")
            break
            
        cluster_assignments = new_cluster_assignments
        
        # Update Step: Recalculate centroids
        for k in range(K):
            cluster_points = X[cluster_assignments == k]
            if len(cluster_points) > 0:
                centroids[k] = np.mean(cluster_points, axis=0)
                
    return cluster_assignments, centroids

# Principal Component Analysis to reduce 11-D data to 2-D for visualization
def get_first_two_pcs(X):
    # Compute Covariance Matrix
    covariance_matrix = np.cov(X.T)
    # Compute Eigenvalues and Eigenvectors
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)
    # Sort eigenvectors by eigenvalues
    sorted_indices = np.argsort(eigenvalues)[::-1]
    top_two_eigenvectors = eigenvectors[:, sorted_indices[:2]]
    # Project data
    X_pca = np.dot(X, top_two_eigenvectors)
    return np.real(X_pca)

if __name__ == "__main__":
    print("Loading WineQT dataset...")
    # 2(a) Read dataset
    df = pd.read_csv('WineQT.csv')

    # Drop target variable 'quality' and irrelevant 'Id'
    features_to_drop = ['Id', 'quality'] if 'Id' in df.columns else ['quality']
    X_df = df.drop(columns=features_to_drop)
    feature_names = X_df.columns.tolist()
    X = X_df.values

    # Standardize features for K-means (distance-based algorithm)
    X_scaled = (X - np.mean(X, axis=0)) / np.std(X, axis=0)

    # 2(b) Apply K-Means
    k_values = [3, 5, 10, 15]
    results = {}

    for K in k_values:
        print(f"Running K-Means for K={K}...")
        assignments, centroids = k_means(X_scaled, K)
        results[K] = {
            'assignments': assignments,
            'centroids': centroids
        }

    # 2(c) Visualization using custom PCA to reduce to 2 dimensions for plotting
    X_pca = get_first_two_pcs(X_scaled)

    plt.figure(figsize=(15, 10))
    for i, K in enumerate(k_values):
        plt.subplot(2, 2, i + 1)
        assignments = results[K]['assignments']
        
        for k in range(K):
            cluster_points = X_pca[assignments == k]
            plt.scatter(cluster_points[:, 0], cluster_points[:, 1], label=f'Cluster {k}', alpha=0.6, s=20)
            
        plt.title(f'K-Means Clustering (K={K})')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        
    plt.tight_layout()
    plt.savefig('Problem2_Clusters.png')
    plt.close()

    # Report cluster sizes and analysis
    with open("Problem2_Analysis.txt", "w") as f:
        f.write("K-Means Clustering Analysis\n")
        f.write("===========================\n\n")
        for K in k_values:
            f.write(f"--- K = {K} ---\n")
            assignments = results[K]['assignments']
            unique, counts = np.unique(assignments, return_counts=True)
            for val, count in zip(unique, counts):
                f.write(f"Cluster {val}: {count} points\n")
            f.write("\n")
            
        f.write("Result Analysis:\n")
        f.write("The K-Means algorithm was applied to the 11 constituents of the WineQT dataset.\n")
        f.write("As the number of initial centroids (K) increases from 3 to 15, the clusters become smaller and more fragmented.\n")
        f.write("PCA was used strictly to project the 11-dimensional clusters down to 2 dimensions for visual inspection.\n")
        f.write("In the visualizations, lower values of K (like K=3 or K=5) show broad, distinct groupings that might correspond to general wine types or major quality categories.\n")
        f.write("Higher values (like K=10 or K=15) show heavy overlap in the 2D projected space, suggesting that they are finding very nuanced local structures or potentially over-segmenting the dataset.\n")

    print("\n[+] Clustering complete.")
    print("[+] Visualizations saved to 'Problem2_Clusters.png'")
    print("[+] Analysis report saved to 'Problem2_Analysis.txt'")

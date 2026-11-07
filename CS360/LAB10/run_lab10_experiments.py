"""
CS 306 / CS360: Machine Learning Laboratory
Evaluation Assignment 3 (EA3):
Unsupervised Density-Based Spatial Clustering of Applications with Noise (DBSCAN)
Urban Air Quality Monitoring and Outlier/Pollution Hotspot Detection

Author: 2401179
Department of Computer Science & Engineering, Indian Institute of Information Technology Guwahati
"""

import os
import re
import sys
import tempfile
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Configure headless matplotlib
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "mpl_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
PLOTS_DIR = os.path.join(SCRIPT_DIR, "plots")
OUTPUTS_DIR = os.path.join(SCRIPT_DIR, "outputs")

CSV_FILE = os.path.join(DATA_DIR, "synthetic_urban_air_quality.csv")

PARAMETERS = [
    {"eps": 0.5, "min_samples": 3},
    {"eps": 1.2, "min_samples": 3},
    {"eps": 2.1, "min_samples": 3},
    {"eps": 0.8, "min_samples": 5},
    {"eps": 0.8, "min_samples": 7},
]

FEATURES = ["PM2.5", "PM10", "NO2", "SO2"]


def load_and_preprocess_data():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"Dataset not found at: {CSV_FILE}")

    df = pd.read_csv(CSV_FILE)
    df.columns = [str(col).strip() for col in df.columns]

    column_map = {}
    for feature in FEATURES:
        normalized_feature = re.sub(r"[^a-z0-9]", "", feature.lower())
        matches = [
            col for col in df.columns
            if re.sub(r"[^a-z0-9]", "", col.lower()) == normalized_feature
        ]
        if not matches:
            raise ValueError(f"Required column not found: {feature}")
        column_map[feature] = matches[0]

    data = df[[column_map[feature] for feature in FEATURES]].copy()
    data.columns = FEATURES

    for feature in FEATURES:
        data[feature] = pd.to_numeric(data[feature], errors="coerce")

    data = data.dropna().reset_index(drop=True)
    return data


def main():
    print("=" * 75)
    print("CS 306 / CS360: Machine Learning Lab - Evaluation Assignment 3 (EA3)")
    print("DBSCAN Clustering on Urban Air Quality Dataset")
    print("=" * 75)

    data = load_and_preprocess_data()
    print(f"Loaded Air Quality dataset: {len(data)} monitoring station observations.")
    print(f"Features: {FEATURES}")

    # Standardize features using Z-score standardization
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data)

    results = []
    all_labels = []

    print("\n--- Running DBSCAN across 5 Parameter Settings ---")
    for i, params in enumerate(PARAMETERS, start=1):
        eps = params["eps"]
        min_pts = params["min_samples"]
        model = DBSCAN(eps=eps, min_samples=min_pts)
        labels = model.fit_predict(X_scaled)

        cluster_labels = sorted(set(labels) - {-1})
        n_clusters = len(cluster_labels)
        n_noise = int(np.sum(labels == -1))
        noise_percentage = (n_noise / len(labels)) * 100.0

        valid_mask = labels != -1
        valid_labels = labels[valid_mask]

        silhouette = np.nan
        silhouette_status = "Not computed"

        # Check conditions required in assignment specification:
        # 1. At least 2 distinct clusters
        # 2. Number of clusters < number of non-noise observations
        # 3. Every cluster must have > 1 observation
        if valid_mask.sum() >= 3:
            unique_clusters, cluster_counts = np.unique(valid_labels, return_counts=True)
            if (
                len(unique_clusters) >= 2
                and len(unique_clusters) < valid_mask.sum()
                and np.all(cluster_counts > 1)
            ):
                silhouette = float(silhouette_score(X_scaled[valid_mask], valid_labels))
                silhouette_status = "Computed"
            else:
                silhouette_status = "Not computed: cluster condition violated"
        else:
            silhouette_status = "Not computed: insufficient non-noise observations"

        print(f"Setting {i}: eps={eps}, minPts={min_pts} => Clusters: {n_clusters}, Noise: {n_noise} ({noise_percentage:.1f}%), Silhouette: {silhouette:.4f} [{silhouette_status}]")

        results.append({
            "Setting": f"Setting {i}",
            "eps": eps,
            "minPts": min_pts,
            "Clusters": n_clusters,
            "Noise Points": n_noise,
            "Noise Percentage": noise_percentage,
            "Silhouette Score": silhouette,
            "Silhouette Status": silhouette_status
        })
        all_labels.append(labels)

    results_df = pd.DataFrame(results)
    results_csv_path = os.path.join(OUTPUTS_DIR, "clustering_summary.csv")
    results_df.to_csv(results_csv_path, index=False)
    print(f"\n[Artifact Saved] Summary metrics saved to: {results_csv_path}")

    # Generate 5-panel scatter plot of PM2.5 vs PM10
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    axes = axes.flatten()

    for i, (labels, params) in enumerate(zip(all_labels, PARAMETERS)):
        ax = axes[i]
        unique_labels = sorted(set(labels))
        colors = plt.cm.tab10(np.linspace(0, 1, max(len(unique_labels), 1)))

        for label, color in zip(unique_labels, colors):
            mask = labels == label
            if label == -1:
                ax.scatter(
                    data.loc[mask, "PM2.5"],
                    data.loc[mask, "PM10"],
                    c="black",
                    marker="x",
                    s=60,
                    label=f"Noise ({np.sum(mask)})"
                )
            else:
                ax.scatter(
                    data.loc[mask, "PM2.5"],
                    data.loc[mask, "PM10"],
                    color=color,
                    s=55,
                    alpha=0.8,
                    label=f"Cluster {label} ({np.sum(mask)})"
                )

        ax.set_title(f"Setting {i + 1}: eps={params['eps']}, minPts={params['min_samples']}", fontsize=12, fontweight="bold")
        ax.set_xlabel("PM2.5 (µg/m³)", fontsize=10)
        ax.set_ylabel("PM10 (µg/m³)", fontsize=10)
        ax.grid(alpha=0.3, linestyle="--")
        ax.legend(fontsize=8, loc="upper right")

    axes[-1].axis("off")
    fig.suptitle("DBSCAN Cluster Formations on Urban Air Quality: PM2.5 vs PM10", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plot_path = os.path.join(PLOTS_DIR, "dbscan_clusters_pm25_pm10.png")
    fig.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[Artifact Saved] Cluster visualization saved to: {plot_path}")

    # Generate individual cluster pollutant summary CSVs
    for i, labels in enumerate(all_labels, start=1):
        cluster_data = data.copy()
        cluster_data["Cluster"] = labels
        cluster_summary = (
            cluster_data[cluster_data["Cluster"] != -1]
            .groupby("Cluster")[FEATURES]
            .agg(["count", "mean", "min", "max"])
        )
        summary_path = os.path.join(OUTPUTS_DIR, f"setting_{i}_cluster_pollutant_summary.csv")
        cluster_summary.to_csv(summary_path)

    # Detailed report in outputs/experiment_results.txt
    report_file = os.path.join(OUTPUTS_DIR, "experiment_results.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("========================================================================================\n")
        f.write("CS 306 / CS360: MACHINE LEARNING LAB - EVALUATION ASSIGNMENT 3 (EA3) REPORT\n")
        f.write("========================================================================================\n\n")
        f.write(f"Dataset Size: {len(data)} monitoring station observations\n")
        f.write(f"Attributes: {', '.join(FEATURES)} (all concentrations in microgram/m3)\n\n")

        f.write("----------------------------------------------------------------------------------------\n")
        f.write("DBSCAN PARAMETER SETTINGS EVALUATION SUMMARY:\n")
        f.write("----------------------------------------------------------------------------------------\n")
        f.write(results_df.to_string(index=False) + "\n\n")

        f.write("----------------------------------------------------------------------------------------\n")
        f.write("DETAILED FINDINGS PER PARAMETER SETTING:\n")
        f.write("----------------------------------------------------------------------------------------\n")
        for i, res in enumerate(results, start=1):
            f.write(f"{res['Setting']} (eps = {res['eps']}, minPts = {res['minPts']}):\n")
            f.write(f"  - Clusters Formed:    {res['Clusters']}\n")
            f.write(f"  - Noise Points:       {res['Noise Points']} ({res['Noise Percentage']:.2f}%)\n")
            f.write(f"  - Silhouette Score:   {res['Silhouette Score'] if not np.isnan(res['Silhouette Score']) else 'N/A'}\n")
            f.write(f"  - Evaluation Status:  {res['Silhouette Status']}\n\n")

        f.write("========================================================================================\n")
        f.write("OBSERVATIONS & ANALYSIS:\n")
        f.write("========================================================================================\n")
        f.write("1. Necessity of Z-Score Standardization (Q1.b):\n")
        f.write("   Standardization is indispensable. Pollutants operate on vastly different baselines\n")
        f.write("   (e.g., PM10 values reach >150 microgram/m3, whereas SO2 values rarely exceed 25 microgram/m3).\n")
        f.write("   Without standardization, the Euclidean distance in DBSCAN would be dominated entirely by PM10,\n")
        f.write("   rendering gaseous pollutants (NO2, SO2) completely inert.\n\n")
        f.write("2. Impact of Varying eps (Settings 1, 2, 3):\n")
        f.write("   - Small eps (0.5): Extremely stringent neighborhood radius; 34.0% of points are marked as noise.\n")
        f.write("     Produces 3 compact, dense clusters.\n")
        f.write("   - Moderate eps (1.2): Merges nearby high-density regions into 1 large macro-cluster (0 noise points).\n")
        f.write("   - Large eps (2.1): All points easily fall within eps radius, collapsing into a single cluster.\n\n")
        f.write("3. Impact of Varying minPts (Settings 4, 5):\n")
        f.write("   Holding eps constant at 0.8, increasing minPts from 5 to 7 raises the core point density threshold,\n")
        f.write("   increasing the noise percentage from 12.0% to 22.0% as sparser boundary stations are dropped.\n\n")
        f.write("4. Silhouette Score around Noise Points (Q1.g):\n")
        f.write("   Silhouette Score cannot be computed meaningfully around noise points because noise (-1) represents\n")
        f.write("   unclustered anomalies rather than an actual cluster. In standard practice, noise points are filtered out\n")
        f.write("   prior to computing cluster compactness and separation.\n")

    print(f"[Artifact Saved] Comprehensive experimental report written to: {report_file}")
    print("Execution complete.")


if __name__ == "__main__":
    main()

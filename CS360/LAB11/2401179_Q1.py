import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


CSV_FILE = r"E:\IIIT G\SEM_5\CS360\LAB10\synthetic_urban_air_quality.csv"
OUTPUT_DIR = "outputs"

PARAMETERS = [
    {"eps": 0.5, "min_samples": 3},
    {"eps": 1.2, "min_samples": 3},
    {"eps": 2.1, "min_samples": 3},
    {"eps": 0.8, "min_samples": 5},
    {"eps": 0.8, "min_samples": 7},
]

FEATURES = ["PM2.5", "PM10", "NO2", "SO2"]

os.makedirs(OUTPUT_DIR, exist_ok=True)

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

scaler = StandardScaler()
X_scaled = scaler.fit_transform(data)

results = []
all_labels = []

for i, params in enumerate(PARAMETERS, start=1):
    model = DBSCAN(eps=params["eps"], min_samples=params["min_samples"])
    labels = model.fit_predict(X_scaled)

    cluster_labels = sorted(set(labels) - {-1})
    n_clusters = len(cluster_labels)
    n_noise = int(np.sum(labels == -1))
    noise_percentage = (n_noise / len(labels)) * 100

    valid_mask = labels != -1
    valid_labels = labels[valid_mask]

    silhouette = np.nan
    silhouette_status = "Not computed"

    if valid_mask.sum() >= 3:
        unique_clusters, cluster_counts = np.unique(valid_labels, return_counts=True)

        if (
            len(unique_clusters) >= 2
            and len(unique_clusters) < valid_mask.sum()
            and np.any(cluster_counts > 1)
            and np.all(cluster_counts > 1)
        ):
            silhouette = silhouette_score(X_scaled[valid_mask], valid_labels)
            silhouette_status = "Computed"
        else:
            silhouette_status = "Not computed: invalid cluster structure after removing noise"
    else:
        silhouette_status = "Not computed: insufficient non-noise observations"

    results.append({
        "Setting": f"Setting {i}",
        "eps": params["eps"],
        "minPts": params["min_samples"],
        "Clusters": n_clusters,
        "Noise Points": n_noise,
        "Noise Percentage": noise_percentage,
        "Silhouette Score": silhouette,
        "Silhouette Status": silhouette_status
    })

    all_labels.append(labels)

results_df = pd.DataFrame(results)
results_df.to_csv(os.path.join(OUTPUT_DIR, "clustering_summary.csv"), index=False)

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
                label="Noise"
            )
        else:
            ax.scatter(
                data.loc[mask, "PM2.5"],
                data.loc[mask, "PM10"],
                color=color,
                s=55,
                alpha=0.8,
                label=f"Cluster {label}"
            )

    ax.set_title(f"eps={params['eps']}, minPts={params['min_samples']}")
    ax.set_xlabel("PM2.5 (µg/m³)")
    ax.set_ylabel("PM10 (µg/m³)")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)

axes[-1].axis("off")

plt.tight_layout()
plot_path = os.path.join(OUTPUT_DIR, "dbscan_clusters_pm25_pm10.png")
plt.savefig(plot_path, dpi=300, bbox_inches="tight")
plt.close()

for i, labels in enumerate(all_labels, start=1):
    cluster_data = data.copy()
    cluster_data["Cluster"] = labels

    cluster_summary = (
        cluster_data[cluster_data["Cluster"] != -1]
        .groupby("Cluster")[FEATURES]
        .agg(["count", "mean", "min", "max"])
    )

    cluster_summary.to_csv(
        os.path.join(OUTPUT_DIR, f"setting_{i}_cluster_pollutant_summary.csv")
    )

headers = [
    "Setting", "eps", "minPts", "Clusters",
    "Noise Points", "Noise %", "Silhouette Score"
]

print("\nClustering Results:\n")
print(results_df.to_string(index=False))

print("\nFiles created:")
print(f"- {os.path.join(OUTPUT_DIR, 'clustering_summary.csv')}")
print(f"- {plot_path}")

for i in range(1, 6):
    print(f"- {os.path.join(OUTPUT_DIR, f'setting_{i}_cluster_pollutant_summary.csv')}")

print(len(data))
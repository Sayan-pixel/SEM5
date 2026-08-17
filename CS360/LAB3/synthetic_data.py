from sklearn.datasets import make_classification, make_moons
import pandas as pd

X1, Y1 = make_classification(
    n_samples=1000,
    n_features=2,
    n_classes=2,
    n_redundant=0,
    random_state=42
)

dataset1 = pd.DataFrame(X1, columns=["feature1", "feature2"])
dataset1["target"] = Y1

X2, Y2 = make_moons(
    n_samples=1000,
    noise=0.2,
    random_state=42
)

dataset2 = pd.DataFrame(X2, columns=["feature1", "feature2"])
dataset2["target"] = Y2

print("Dataset 1:")
print(dataset1.head())

print("\nDataset 2:")
print(dataset2.head())

dataset1.to_csv("dataset1.csv", index=False)
dataset2.to_csv("dataset2.csv", index=False)
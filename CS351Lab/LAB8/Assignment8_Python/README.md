# Assignment 8: Hadoop MapReduce with Python & Streaming API

This folder contains the solutions for **CS351 - Assignment 8 (Hadoop Streaming)**.

## Directory Structure & Task Mapping

- **`task1_simulation/`**:
  - **Section 2**: Word Count MapReduce Simulation using standard UNIX pipes (`cat | mapper.py | sort | reducer.py`) and execution on Hadoop using the Hadoop Streaming jar.
  - Files to be added: `mapper.py`, `reducer.py`, input text files.

- **`task2_distinct_words/`**:
  - **Section 3 (Problem 1)**: Distinct words finder with data cleaning (all punctuation stripped, all words converted to lowercase).
  - Files to be added: `mapper.py`, `reducer.py`.

- **`task3_combiner/`**:
  - **Section 3 (Problem 2)**: Extended Word Count featuring a Combiner (`-combiner combiner.py`) to optimize local aggregation before shuffle.
  - Files to be added: `mapper.py`, `combiner.py`, `reducer.py`.

- **`task4_iris_kmeans/`**:
  - **Section 3 (Problem 3)**: 1-Iteration K-Means clustering algorithm on the Iris dataset to compute Euclidean distance to 3 initial candidate centroids and update candidate points by taking the average.
  - Files to be added: `iris_mapper.py`, `iris_reducer.py`, `iris.data`.

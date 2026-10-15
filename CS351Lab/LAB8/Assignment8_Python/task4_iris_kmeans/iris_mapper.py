#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys
import math

# Candidate centroids defined in Table 4 of the assignment
CANDIDATE_CENTROIDS = [
    (5.8, 4.0),  # Candidate 0
    (6.1, 2.8),  # Candidate 1
    (6.3, 2.7)   # Candidate 2
]

def calculate_euclidean_distance(point_x, point_y, centroid_x, centroid_y):
    return math.sqrt((point_x - centroid_x) ** 2 + (point_y - centroid_y) ** 2)

def map_points_to_nearest_centroid():

    for raw_line in sys.stdin:
        cleaned_line = raw_line.strip()
        if not cleaned_line:
            continue

        columns = cleaned_line.split(',')
        if len(columns) < 2:
            continue

        try:
            # Extract Sepal Length and Sepal Width as requested by the assignment
            sepal_length = float(columns[0])
            sepal_width = float(columns[1])
        except ValueError:
            # Skip invalid header or corrupt data lines
            continue

        # Find the candidate centroid with the minimal Euclidean distance
        closest_centroid_id = -1
        minimum_distance = float('inf')

        for centroid_id, (centroid_x, centroid_y) in enumerate(CANDIDATE_CENTROIDS):
            distance = calculate_euclidean_distance(sepal_length, sepal_width, centroid_x, centroid_y)
            if distance < minimum_distance:
                minimum_distance = distance
                closest_centroid_id = centroid_id

        # Emit intermediate record: centroid_id, x, y, count=1
        print("{0},{1},{2},1".format(closest_centroid_id, sepal_length, sepal_width))

if __name__ == "__main__":
    map_points_to_nearest_centroid()

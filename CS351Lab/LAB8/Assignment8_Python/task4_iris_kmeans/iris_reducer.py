#!/usr/bin/env python3
# Name: Sayan Shit
# Roll No: 2401179

import sys

def reduce_and_update_centroids():

    current_centroid_id = None
    sum_sepal_length = 0.0
    sum_sepal_width = 0.0
    total_assigned_points = 0

    for raw_line in sys.stdin:
        cleaned_line = raw_line.strip()
        if not cleaned_line:
            continue

        parts = cleaned_line.split(',')
        if len(parts) < 4:
            continue

        try:
            centroid_id = int(parts[0])
            point_x = float(parts[1])
            point_y = float(parts[2])
            point_count = int(parts[3])
        except ValueError:
            continue

        # If matching current cluster, accumulate coordinates and point count
        if current_centroid_id == centroid_id:
            sum_sepal_length += point_x
            sum_sepal_width += point_y
            total_assigned_points += point_count
        else:
            # When cluster transitions, compute and emit average of previous cluster
            if current_centroid_id is not None and total_assigned_points > 0:
                new_sepal_length = sum_sepal_length / total_assigned_points
                new_sepal_width = sum_sepal_width / total_assigned_points
                print("Candidate_{0},{1:.4f},{2:.4f},PointsAssigned={3}".format(
                    current_centroid_id, new_sepal_length, new_sepal_width, total_assigned_points
                ))

            # Initialize new cluster tracking
            current_centroid_id = centroid_id
            sum_sepal_length = point_x
            sum_sepal_width = point_y
            total_assigned_points = point_count

    # Emit the last accumulated candidate point
    if current_centroid_id is not None and total_assigned_points > 0:
        new_sepal_length = sum_sepal_length / total_assigned_points
        new_sepal_width = sum_sepal_width / total_assigned_points
        print("Candidate_{0},{1:.4f},{2:.4f},PointsAssigned={3}".format(
            current_centroid_id, new_sepal_length, new_sepal_width, total_assigned_points
        ))

if __name__ == "__main__":
    reduce_and_update_centroids()

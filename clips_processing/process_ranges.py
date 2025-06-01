import sys
import os
import pickle
import json
from plot import save_plot

import numpy as np

def detect_changes_point(time_series, window_size, threshold):
    """
    Detects abrupt changes in a time series by comparing the window mean to the current value.
    Uses NumPy for calculations and returns integer indices.

    Args:
        time_series (np.ndarray): The input time series as a NumPy array.
        window_size (int): The size of the moving window.
        threshold (float): The maximum allowed percentage change.

    Returns:
        list: A list of integer indices where abrupt changes were detected.
    """
    abrupt_change_indices = []
    
    # Ensure time_series is a NumPy array
    if not isinstance(time_series, np.ndarray):
        time_series = np.asarray(time_series)

    # We start the loop from window_size because we need at least 'window_size'
    # elements before the current element to form the first window.
    for i in range(window_size, len(time_series)):
        current_value = time_series[i]
        
        # Define the window using NumPy slicing
        window = time_series[i - window_size : i]
        window_mean = np.mean(window)

        if current_value == 0 or window_mean == 0:  # Avoid division by zero
            continue # Move to the next iteration

        percentage_change = np.abs((current_value - window_mean) / window_mean)

        if percentage_change > threshold:
            # print(f"id {i}: %: {percentage_change} v: {current_value}  w:{window}")
            abrupt_change_indices.append(i)

    return abrupt_change_indices

def process_ranges(data_path):
    with open (data_path, 'rb') as f:
        data = pickle.load(f)
    with open ("options.json", "r") as f:
        options = json.load(f)

    skip_frames = options["skip_frames"]
    low_threshold = options["low_threshold"]
    high_threshold = options["high_threshold"]
    change_point_threshold = options["change_point_threshold"]
    window_size = options["window_size"]
    
    changes_points = detect_changes_point(data, window_size= window_size, threshold= change_point_threshold)

    # print(changes_points)

    split_gap = 3
    data_ranges = []
    start = changes_points[0]
    data_ranges.append((0, start))
    for i in range(1, len(changes_points)):
        if changes_points[i] - changes_points[i-1] > split_gap:
            data_ranges.append((start,changes_points[i]))
            start = changes_points[i]+1

    if changes_points[-1] != len(data):
        data_ranges.append((start,len(data)))

    clean_data = []
    for data_range in data_ranges:
        range_mean = np.mean(data[data_range[0]:data_range[1]])
        if low_threshold < range_mean < high_threshold:
            clean_data.append(data_range)

    # print(data_ranges)
    frame_ranges = [[r[0]*(skip_frames+1),r[1]*(skip_frames+1) + skip_frames] for r in clean_data] # Leva em consideração os frames pulados
    # print(frame_ranges)

    processed_folder = os.path.dirname(data_path)
    with open (os.path.join(processed_folder, "ranges.pkl"), "wb") as f:
        pickle.dump(frame_ranges, f)

    print(f"Total ranges = {len(data_ranges)}")

    save_plot(processed_folder)
    
if __name__ == "__main__":
    data_path = sys.argv[-1]
    process_ranges(data_path)
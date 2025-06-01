import matplotlib.pyplot as plt
import numpy as np
import pickle
import json
import os
import sys

def save_plot(folder_path):

    with open(os.path.join(folder_path, "movement.pkl"), "rb") as f:
        time_series = pickle.load(f)

    with open(os.path.join(folder_path, "cap_data.pkl"), "rb") as f:
        cap_data = pickle.load(f)
        frame_count = cap_data["frame_count"]
        fps = cap_data["fps"]

    with open(os.path.join(folder_path, "ranges.pkl"), "rb") as f:
        ranges = pickle.load(f)

    with open("options.json", "r") as f:
        options = json.load(f)
        h_lines = [options["low_threshold"], options["high_threshold"]]
        skip_frames = options["skip_frames"]
        jump_seconds = options["jump_seconds"]
        y_limit = options["y_limit"]

    frame_index = np.arange(0, len(time_series)*(skip_frames+1), skip_frames+1)

    # Calculate total video duration
    total_seconds = round(frame_count / fps)

    time_labels_seconds = np.arange(0, total_seconds + 1, jump_seconds)
    x_tick_pos = [(time_sec/total_seconds)* frame_index[-1] for time_sec in time_labels_seconds]
    x_tick_labels = [f"{sec//60}:{sec%60:02d}\n{int(x_tick)}" for sec, x_tick in zip(time_labels_seconds, x_tick_pos)]
    # x_tick_labels = [f"{sec//60}:{sec%60:02d}" for sec in time_labels_seconds]

    # Plot
    plt.figure(figsize= (min(len(time_labels_seconds),300),8))
    plt.plot(frame_index, time_series)
    if y_limit:
        plt.ylim(y_limit)
    # if x_limit:
    #     plt.xlim(x_limit)
    for line in h_lines:
        plt.axhline(y=line, color='r', linestyle='-')
    # for line in v_lines:
    #     plt.axvline(x=line, color='r', linestyle='-')
    for range in ranges:
        plt.axvspan(*range, color='green', alpha = 0.5)
        plt.axvline(x=range[-1], color='g', linestyle='-')
        
    plt.xticks(x_tick_pos, x_tick_labels, rotation=25, size=10)
    plt.xlabel('Time (MM:SS)')

    plt.title("Movement", fontsize=16)
    plt.grid(True)
    plt.tight_layout()

    save_path = os.path.join(folder_path, "movement.png")
    plt.savefig(save_path)
    print(f"Image plot saved at {save_path}")

if __name__ == "__main__":
    folder_path = sys.argv[-1]
    save_plot(folder_path)
import os
import sys
import cv2
import json
import pickle

from create_processed_folder import create_processed_folder


def merge_ranges(frame_ranges):
    # Merge if end[n] = start[n+1]
    new_frame_ranges = [frame_ranges[0]]
    for frame_range in frame_ranges[1:]:
        if frame_range[0] == new_frame_ranges[-1][1] +1:
            new_frame_ranges[-1][1] = frame_range[1]
        else:
            new_frame_ranges.append(frame_range)
    return new_frame_ranges


def save_frames(video_path):
    processed_folder = create_processed_folder(video_path)
    review_path = os.path.join(processed_folder, "video_review_progress.json")
    save_folder = os.path.join(processed_folder, "frames")
    if not os.path.exists(save_folder):
        print(f'Criando diretório {save_folder}')
        os.mkdir(save_folder)

    points_path = os.path.join(processed_folder, "points.pkl")
    with open(points_path, "rb") as f:
        points = pickle.load(f)
    x_coords, y_coords = zip(*points)

    # Get bounding box
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)

    with open(review_path, "r") as f:
        frame_ranges = json.load(f)["validated_ranges"]

    frame_ranges = merge_ranges(frame_ranges)

    with open("options.json", "r") as f:
        skip_frames_save = json.load(f)["skip_frames_save"]

    cap = cv2.VideoCapture(video_path)
    for frame_range in frame_ranges:
        current_frame_index = frame_range[0]
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index)

        for frame_index in range(frame_range[0], frame_range[1], skip_frames_save):
            while frame_index != current_frame_index:
                cap.grab() # Faster than set in small gaps, faster than read when not decoding
                current_frame_index += 1
            _, frame = cap.read()
            cv2.imwrite(os.path.join(save_folder, f"{current_frame_index}.jpg"), frame[y_min:y_max, x_min:x_max]) # Save Crop
            current_frame_index += 1


if __name__ == "__main__":
    video_path = sys.argv[-1]
    save_frames(video_path)
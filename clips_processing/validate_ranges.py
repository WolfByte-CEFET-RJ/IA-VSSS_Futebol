import cv2
import json
import os
import sys
import pickle

from create_processed_folder import create_processed_folder
from save_frames import save_frames


WINDOW_NAME = 'Frame'

def load_progress(save_path):
    with open(save_path, 'r') as f:
        try:
            progress = json.load(f)
            return progress.get('frame_ranges'), progress.get('validated_ranges'), progress.get('current_range_index'), progress.get('complet')
        except json.JSONDecodeError:
            print("Error decoding save file. Starting fresh.")
            return 1

def save_progress(save_path, frame_ranges, validated_ranges, current_range_index, complet = False):
    progress = {'frame_ranges': frame_ranges, 'validated_ranges': validated_ranges, 'current_range_index': current_range_index, 'complet':complet}
    with open(save_path, 'w') as f:
        json.dump(progress, f)
    print(f"💾 Progress saved to {save_path}")


def validate_ranges(video_path):
    cap = cv2.VideoCapture(video_path)

    processed_path = create_processed_folder(video_path)
    save_path = os.path.join(processed_path, "video_review_progress.json")

    with open(os.path.join(processed_path, "ranges.pkl"), "rb") as f:
        frame_ranges = pickle.load(f)

    validated_ranges = []
    current_range_index = 0
    
    if os.path.exists(save_path):
        answer = input("Load previous progress? (y/n): ").lower()
        if answer == 'y':
            frame_ranges, validated_ranges, current_range_index, complet = load_progress(save_path)
            print("Loaded previous progress.")
            if complet == True:
                print("Loaded file is already complet!")
                return 0
        else:
            print("Starting fresh.")
    else:
        print("No previous progress found. Starting fresh.")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # fps = cap.get(cv2.CAP_PROP_FPS)

    speed = 5
    manual_step = 1
    review_mode = "auto"  # Can be "auto" or "manual"
    early_exit = False
    # print(frame_ranges)

    while current_range_index < len(frame_ranges) and not early_exit:
        start, end = frame_ranges[current_range_index]

        # Validate bounds
        if start < 0 or end >= total_frames or start >= end:
            print(f"Invalid range: [{start}, {end}]")
            current_range_index += 1
            continue

        print(f"Reviewing range: [{start}, {end}] - ", end="")
        if review_mode == "auto":
            print("Press 'z' to validate, 'x' to skip, 'ESC' to exit, 's' to switch to manual.")
        elif review_mode == "manual":
            print("Press 'z' to validate, 'x' to skip, 'ESC' to exit, 'a' to go back, 'd' to go forward, 'space' to split, 's' to switch to auto.")

        cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        current_frame = start
        range_length = end - start + 1

        # Create a resizable window
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        while True:
            if current_frame > end and review_mode == "auto":
                current_frame = start
                cap.set(cv2.CAP_PROP_POS_FRAMES, start)
            elif current_frame < start and review_mode == "manual":
                current_frame = start
                cap.set(cv2.CAP_PROP_POS_FRAMES, start)

            ret, frame = cap.read()
            if not ret:
                break

            # Calculate relative frame number
            relative_pos = current_frame - start + 1
            overlay_text = f"{relative_pos}/{range_length}   {current_frame}"

            # Put the overlay on the frame
            cv2.putText(frame, overlay_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('Frame', frame)

            key = cv2.waitKey(speed if review_mode == "auto" else 0) & 0xFF

            if key == ord('z'):
                validated_ranges.append([start, end])
                print(f"✅ Validated range: [{start}, {end}]")
                break
            elif key == ord('x'):
                print(f"❌ Skipped range: [{start}, {end}]")
                break
            elif key == 27:  # ESC key
                early_exit = True
                save_progress(save_path, frame_ranges, validated_ranges, current_range_index)
                break
            elif key == ord('s'):
                review_mode = "auto" if review_mode == "manual" else "manual"
                print(f"Switched to {review_mode} review mode.")
                print("Press 'd' to go forward, 'a' to go back, 'space' to split, 's' to switch to auto.")
            elif review_mode == "manual":
                if key == ord('a'):
                    current_frame = max(start, current_frame - manual_step)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                elif key == ord('d'):
                    current_frame = min(end, current_frame + manual_step)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                elif key == ord(' '):
                    if start < current_frame < end:
                        new_range1 = [start, current_frame]
                        new_range2 = [current_frame + 1, end]
                        frame_ranges[current_range_index] = new_range1
                        frame_ranges.insert(current_range_index + 1, new_range2)
                        print(f"✂️ Split range [{start}, {end}] into [{new_range1[0]}, {new_range1[1]}] and [{new_range2[0]}, {new_range2[1]}].")
                        end = current_frame
                        # print(frame_ranges)
                        review_mode = "auto"
                    else:
                        print("Cannot split at the boundary.")

            elif review_mode == "auto":
                current_frame += 1

        if early_exit:
            print("🚪 Exiting early due to ESC key.")
            break

        current_range_index += 1

    cap.release()
    cv2.destroyAllWindows()

    if current_range_index == len(frame_ranges):
        save_progress(save_path, frame_ranges, validated_ranges, current_range_index, True)
        print("🎉 All work is done!")
        save = input("Save now? y/n")
        if save == "y":
            save_frames(video_path)

    # print("\nValidated Ranges:", validated_ranges)
    # print("Total Ranges:", frame_ranges)

if __name__ == "__main__":
    video_path = sys.argv[-1]
    validate_ranges(video_path)

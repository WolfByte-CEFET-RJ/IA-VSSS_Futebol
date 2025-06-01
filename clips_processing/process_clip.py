from process_movement import process_movement
from process_ranges import process_ranges
from validate_ranges import validate_ranges
import sys

def process_clip(clip_path):
    print("Processing Movement.")
    movement_path = process_movement(clip_path)
    print("Processing Ranges.")
    process_ranges(movement_path)
    validate = input("Validate clip now? (y/n)").lower()
    if validate == "y":
        validate_ranges(clip_path)

if __name__ == "__main__":
    clip_path = sys.argv[-1]
    process_clip(clip_path)
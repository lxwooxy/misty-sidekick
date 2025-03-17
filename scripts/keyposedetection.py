import cv2
import numpy as np
import os
from ultralytics import YOLO

# Define keypoint indices for the head
HEAD_KEYPOINTS = [0, 1, 2, 3, 4]  # Nose, eyes, and ears

# Load YOLOv8 Pose model
model = YOLO("yolov8l-pose.pt")

# Directory containing images
image_dir = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/Misty-Python-SDK/imagetest"
output_dir = os.path.join(image_dir, "processed_head")
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

# Directory for saving cropped head images
head_output_dir = os.path.join(output_dir, "heads")
os.makedirs(head_output_dir, exist_ok=True)

def crop_and_save_head(image, keypoints, filename, person_index):
    """Crop the head region using keypoints and save the image."""
    keypoints = np.array(keypoints, dtype=np.int32)

    # Get head-related keypoints
    head_points = keypoints[HEAD_KEYPOINTS]

    # Ignore invalid detections
    if np.any(head_points < 0):
        return

    # Get bounding box coordinates
    x_min, y_min = np.min(head_points, axis=0)
    x_max, y_max = np.max(head_points, axis=0)

    # Adjust padding: More on the right and bottom
    pad_x_left = 10
    pad_x_right = 30
    pad_y_top = 10
    pad_y_bottom = 40

    x_min = max(0, x_min - pad_x_left)
    y_min = max(0, y_min - pad_y_top)
    x_max = min(image.shape[1], x_max + pad_x_right)
    y_max = min(image.shape[0], y_max + pad_y_bottom)

    # Crop the head region
    head_crop = image[y_min:y_max, x_min:x_max]

    if head_crop.size == 0:
        return  # Skip if the crop is empty

    # Save the cropped head image
    head_filename = f"{os.path.splitext(filename)[0]}_head_{person_index}.png"
    head_path = os.path.join(head_output_dir, head_filename)
    cv2.imwrite(head_path, head_crop)
    print(f"Saved cropped head: {head_path}")

# Process each image in the directory
for filename in os.listdir(image_dir):
    if filename.lower().endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(image_dir, filename)
        image = cv2.imread(image_path)

        if image is None:
            print(f"Skipping {filename}, could not read image.")
            continue

        # Run YOLOv8 Pose model
        results = model(image)

        # Process each detected person
        for person_index, result in enumerate(results):
            for keypoints in result.keypoints.xy:
                if keypoints is not None:
                    crop_and_save_head(image, keypoints, filename, person_index)

print("Processing complete.")
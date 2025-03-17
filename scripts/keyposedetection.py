import cv2
import numpy as np
import os
from ultralytics import YOLO


def draw_x_on_person(image, keypoints):
    """Draw an 'X' on the detected person based on keypoints."""
    for kp in keypoints:
        x, y = int(kp[0]), int(kp[1])
        if x > 0 and y > 0:  # Ensure keypoint is valid
            cv2.line(image, (x - 10, y - 10), (x + 10, y + 10), (0, 0, 255), 2)
            cv2.line(image, (x - 10, y + 10), (x + 10, y - 10), (0, 0, 255), 2)

# Load YOLOv8 Pose model
model = YOLO("yolov8l-pose.pt")

# Directory containing images
image_dir = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/Misty-Python-SDK/groupimages"
output_dir = os.path.join(image_dir, "processed_pose")
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

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

        # Mark 'X' on detected people
        for result in results:
            for keypoints in result.keypoints.xy:
                if keypoints is not None:
                    draw_x_on_person(image, keypoints)

        # Save the processed image
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, image)
        print(f"Processed and saved: {output_path}")

print("Processing complete.")

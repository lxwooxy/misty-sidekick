import cv2
import numpy as np
import os
from ultralytics import YOLO

# Define colors for different body parts
COLOR_HEAD = (0, 255, 0)     # Green for head (nose, eyes, ears)
COLOR_BODY = (0, 0, 255)     # Red for body (neck, shoulders, hips)
COLOR_LIMBS = (128, 0, 128)  # Purple for arms and upper legs
COLOR_ANKLES = (255, 0, 0)   # Blue for ankles


def draw_x_on_person(image, keypoints):
    """Draw an 'X' on keypoints with different colors for body parts."""
    keypoints = np.array(keypoints, dtype=np.int32)
    
    for i, (x, y) in enumerate(keypoints):
        if x > 0 and y > 0:
            # Determine color based on keypoint index
            if i in [0, 1, 2, 3, 4]:  # Nose, eyes, ears -> Head
                color = COLOR_HEAD
            elif i in [5, 6, 11, 12]:  # Shoulders and hips -> Body
                color = COLOR_BODY
            elif i in [7, 8, 9, 10, 13, 14]:  # Arms and upper legs -> Limbs
                color = COLOR_LIMBS
            elif i in [15, 16]:  # Ankles -> Blue
                color = COLOR_ANKLES
            
            cv2.line(image, (x - 10, y - 10), (x + 10, y + 10), color, 2)
            cv2.line(image, (x - 10, y + 10), (x + 10, y - 10), color, 2)

# Load YOLOv8 Pose model
model = YOLO("yolov8l-pose.pt")

# Directory containing images
image_dir = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/Misty-Python-SDK/imagetest"
output_dir = os.path.join(image_dir, "processed")
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

# Process each image in the directory
for filename in os.listdir(image_dir):
    if filename.lower().endswith((".jpg", "png", ".jpeg")):
        image_path = os.path.join(image_dir, filename)
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Skipping {filename}, could not read image.")
            continue

        # Run YOLOv8 Pose model
        results = model(image)

        # Draw X on keypoints
        for result in results:
            for keypoints in result.keypoints.xy:
                if keypoints is not None:
                    draw_x_on_person(image, keypoints)

        # Save the processed image
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, image)
        print(f"Processed and saved: {output_path}")

print("Processing complete.")

# Directory containing images
image_dir = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/covfefe/Assets/images3"
import cv2
import numpy as np
import os
from ultralytics import YOLO

# Define keypoint mappings with labels and colors
KEYPOINT_MAPPING = {
    0: {"label": "Nose", "color": (0, 255, 0)},
    1: {"label": "Left Eye", "color": (0, 255, 0)},
    2: {"label": "Right Eye", "color": (0, 255, 0)},
    3: {"label": "Left Ear", "color": (0, 255, 0)},
    4: {"label": "Right Ear", "color": (0, 255, 0)},
    5: {"label": "Left Shoulder", "color": (0, 0, 255)},
    6: {"label": "Right Shoulder", "color": (0, 0, 255)},
    7: {"label": "Left Elbow", "color": (128, 0, 128)},
    8: {"label": "Right Elbow", "color": (128, 0, 128)},
    9: {"label": "Left Wrist", "color": (128, 0, 128)},
    10: {"label": "Right Wrist", "color": (128, 0, 128)},
    11: {"label": "Left Hip", "color": (0, 0, 255)},
    12: {"label": "Right Hip", "color": (0, 0, 255)},
    13: {"label": "Left Knee", "color": (128, 0, 128)},
    14: {"label": "Right Knee", "color": (128, 0, 128)},
    15: {"label": "Left Ankle", "color": (255, 0, 0)},
    16: {"label": "Right Ankle", "color": (255, 0, 0)}
}


def draw_x_on_person(image, keypoints):
    """Draw an 'X' on keypoints with different colors for body parts."""
    keypoints = np.array(keypoints, dtype=np.int32)
    
    for i, (x, y) in enumerate(keypoints):
        if x > 0 and y > 0:
            color = KEYPOINT_MAPPING.get(i, {"color": (255, 255, 255)})["color"]
            cv2.line(image, (x - 10, y - 10), (x + 10, y + 10), color, 2)
            cv2.line(image, (x - 10, y + 10), (x + 10, y - 10), color, 2)

# Load YOLOv8 Pose model
model = YOLO("yolov8l-pose.pt")


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

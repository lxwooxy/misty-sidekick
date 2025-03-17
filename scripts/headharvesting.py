import cv2
import numpy as np
import os
from ultralytics import YOLO

# Define keypoint indices for the head
NOSE = 0
LEFT_EYE = 1
RIGHT_EYE = 2
LEFT_EAR = 3
RIGHT_EAR = 4

HEAD_KEYPOINTS = [NOSE, LEFT_EYE, RIGHT_EYE, LEFT_EAR, RIGHT_EAR]

# Load YOLOv8 Pose model
model = YOLO("yolov8l-pose.pt")

# Directory containing images
image_dir = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/covfefe/Assets/images3"
output_dir = os.path.join(image_dir, "processed_head")
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

# Directory for saving cropped head images
head_output_dir = os.path.join(output_dir, "heads")
os.makedirs(head_output_dir, exist_ok=True)

def crop_and_save_head(image, keypoints, filename, person_index):
    """Dynamically crop the head using facial keypoints and save the image."""
    
    print(f"crop called with {person_index}")
    keypoints = np.array(keypoints, dtype=np.int32)
    print(f"Size of keypoints: {len(keypoints)}")
    # Extract head-related keypoints
    head_points = keypoints[HEAD_KEYPOINTS]

    # Ignore invalid detections
    valid_points = head_points[(head_points[:, 0] > 0) & (head_points[:, 1] > 0)]
    if valid_points.shape[0] < 2:
        return  # Not enough points to define a head crop

    # Determine head bounding box
    x_min, y_min = np.min(valid_points, axis=0)
    x_max, y_max = np.max(valid_points, axis=0)

    # **Case 1: Full face detected (both eyes, ears, and nose)**
    if all(keypoints[i][0] > 0 for i in HEAD_KEYPOINTS):
        print(f"full head detected for {person_index}")
        # Expand width using ears
        x_min, x_max = keypoints[LEFT_EAR][0]+60, keypoints[RIGHT_EAR][0]-60
        # Expand height using nose and eyes
        y_min -= 200  # Small padding for forehead
        y_max += 200  # Expand downward for chin

    # **Case 2: Head turned (one eye, one ear visible)**
    elif keypoints[LEFT_EYE][0] > 0 and keypoints[LEFT_EAR][0] > 0:
        # Face turned to the right
        x_center = keypoints[LEFT_EAR][0]
        x_min, x_max = x_center - 300, x_center + 200
        y_min -= 200
        y_max += 200

    elif keypoints[RIGHT_EYE][0] > 0 and keypoints[RIGHT_EAR][0] > 0:
        # Face turned to the left
        x_center = keypoints[RIGHT_EAR][0]
        x_min, x_max = x_center - 300, x_center + 200
        y_min -= 200
        y_max += 200

    # Ensure cropping does not go outside the image bounds
    x_min = max(0, x_min)
    y_min = max(0, y_min)
    x_max = min(image.shape[1], x_max)
    y_max = min(image.shape[0], y_max)
    
    # Ensure x_min < x_max and y_min < y_max
    x_min, x_max = sorted([x_min, x_max])
    y_min, y_max = sorted([y_min, y_max])

    
    print(f"xmin max: {x_min, x_max}, ymin max: {y_min, y_max}")

    # Crop the head region
    head_crop = image[y_min:y_max, x_min:x_max]

    if head_crop.size == 0:
        print(f"cropsize was 0")
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
        print(f"length of results0 = {len(results[0])}")

        # Process each detected person
        for result in results:
            person_index = 0
            for keypoints in result.keypoints.xy:
                if keypoints is not None and len(keypoints) != 0:
                    
                    crop_and_save_head(image, keypoints, filename, person_index)
                    person_index += 1
                else:
                    print(f"keypoints was none for {image_path}")

print("Processing complete.")

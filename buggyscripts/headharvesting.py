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
image_dir = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/misty-sidekick/zgroupimages"
head_output_dir = os.path.join(image_dir, "processed_head")
os.makedirs(head_output_dir, exist_ok=True)  # Ensure output directory exists


def determine_pose_type(keypoints):
    has_nose = keypoints[NOSE][0] > 0
    has_both_eyes = keypoints[LEFT_EYE][0] > 0 and keypoints[RIGHT_EYE][0] > 0
    has_both_ears = keypoints[LEFT_EAR][0] > 0 and keypoints[RIGHT_EAR][0] > 0
    has_one_eye = keypoints[LEFT_EYE][0] > 0 or keypoints[RIGHT_EYE][0] > 0
    has_shoulders = keypoints[5][0] > 0 and keypoints[6][0] > 0

    if has_both_eyes or has_both_ears:
        return "frontal"
    elif has_one_eye or has_nose:
        return "side"
    elif has_shoulders:
        return "back"
    return "unknown"

def save_crop(image, x_min, x_max, y_min, y_max, filename, person_index):
    if x_max <= x_min or y_max <= y_min:
        return
    head_crop = image[y_min:y_max, x_min:x_max]
    if head_crop.size == 0:
        return
    head_filename = f"{os.path.splitext(filename)[0]}_head_{person_index}.png"
    head_path = os.path.join(head_output_dir, head_filename)
    cv2.imwrite(head_path, head_crop)
    print(f"Saved cropped head: {head_path}")


def crop_frontal_head(image, keypoints, filename, person_index):
    head_points = keypoints[HEAD_KEYPOINTS]
    valid_points = head_points[(head_points[:, 0] > 0) & (head_points[:, 1] > 0)]
    if valid_points.shape[0] < 2:
        return

    head_center = np.mean(valid_points, axis=0).astype(int)
    
    def dist(a, b):
        if keypoints[a][0] > 0 and keypoints[b][0] > 0:
            return np.linalg.norm(keypoints[a] - keypoints[b])
        return None
    
    ref_dist = dist(LEFT_EAR, RIGHT_EAR) or dist(LEFT_EYE, RIGHT_EYE) or 100
    crop_size = int(ref_dist * 2.5)
    
    x_min = max(0, head_center[0] - crop_size // 2)
    x_max = min(image.shape[1], head_center[0] + crop_size // 2)
    y_min = max(0, head_center[1] - crop_size // 2)
    y_max = min(image.shape[0], head_center[1] + crop_size // 2)

    save_crop(image, x_min, x_max, y_min, y_max, filename, person_index)

def crop_back_view(image, keypoints, filename, person_index):
    # Use midpoint of shoulders as head base
    if keypoints[5][0] <= 0 or keypoints[6][0] <= 0:
        return

    center = ((keypoints[5] + keypoints[6]) / 2).astype(int)

    shoulder_dist = np.linalg.norm(keypoints[5] - keypoints[6])
    crop_w = int(shoulder_dist * 1.5)
    crop_h = int(shoulder_dist * 2.0)

    x_min = max(0, center[0] - crop_w // 2)
    x_max = min(image.shape[1], center[0] + crop_w // 2)
    y_max = center[1]
    y_min = max(0, y_max - crop_h)

    save_crop(image, x_min, x_max, y_min, y_max, filename, person_index)

def crop_back_view(image, keypoints, filename, person_index):
    # Use midpoint of shoulders as head base
    if keypoints[5][0] <= 0 or keypoints[6][0] <= 0:
        return

    center = ((keypoints[5] + keypoints[6]) / 2).astype(int)

    shoulder_dist = np.linalg.norm(keypoints[5] - keypoints[6])
    crop_w = int(shoulder_dist * 1.5)
    crop_h = int(shoulder_dist * 2.0)

    x_min = max(0, center[0] - crop_w // 2)
    x_max = min(image.shape[1], center[0] + crop_w // 2)
    y_max = center[1]
    y_min = max(0, y_max - crop_h)

    save_crop(image, x_min, x_max, y_min, y_max, filename, person_index)

def crop_side_profile(image, keypoints, filename, person_index):
    # Check visibility of facial keypoints
    left_visible = any(keypoints[i][0] > 0 for i in [LEFT_EYE, LEFT_EAR])
    right_visible = any(keypoints[i][0] > 0 for i in [RIGHT_EYE, RIGHT_EAR])

    if left_visible and not right_visible:
        # Facing right → use left eye/ear as anchor
        anchor = next(keypoints[i] for i in [LEFT_EYE, LEFT_EAR] if keypoints[i][0] > 0)
        direction = "right"
    elif right_visible and not left_visible:
        # Facing left → use right eye/ear as anchor
        anchor = next(keypoints[i] for i in [RIGHT_EYE, RIGHT_EAR] if keypoints[i][0] > 0)
        direction = "left"
    else:
        return  # ambiguous

    anchor = anchor.astype(int)
    box_size = 400

    if direction == "right":
        x_min = max(0, anchor[0] - int(box_size * 0.9))
        x_max = min(image.shape[1], anchor[0] + int(box_size * 0.1))
    else:
        x_min = max(0, anchor[0] - int(box_size * 0.1))
        x_max = min(image.shape[1], anchor[0] + int(box_size * 0.9))

    y_min = max(0, anchor[1] - box_size // 2)
    y_max = min(image.shape[0], anchor[1] + box_size // 2)

    save_crop(image, x_min-300, x_max-300, y_min, y_max, filename, person_index)

def crop_and_save_head(image, keypoints, filename, person_index):
    keypoints = np.array(keypoints, dtype=np.int32)
    pose_type = determine_pose_type(keypoints)

    if pose_type == "frontal":
        crop_frontal_head(image, keypoints, filename, person_index)
    elif pose_type == "side":
        crop_side_profile(image, keypoints, filename, person_index)
    elif pose_type == "back":
        crop_back_view(image, keypoints, filename, person_index)
    else:
        print(f"Pose unknown for person {person_index} in {filename}")


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

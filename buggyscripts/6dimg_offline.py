import cv2
import torch

import sys
import os

from sixdrepnet import SixDRepNet

import numpy as np
import pandas as pd

# Function to classify head pose
def classify_head_pose(yaw, pitch):
    if abs(yaw) < 15:
        return "Frontal"
    elif yaw < -15:
        return "Right"
    elif yaw > 15:
        return "Left"
    elif pitch > 20:
        return "Away"
    return "Unknown"

output_folder = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/misty-sidekick/buggyscripts/poseaxis"
os.makedirs(output_folder, exist_ok=True)

# Create csv to store head pose data, append if it already exists 
# Filename, yaw, pitch, roll
csv = os.path.join(output_folder, "head_pose_predictions.csv")
if not os.path.exists(csv):
    df = pd.DataFrame(columns=["Filename", "Yaw", "Pitch", "Roll", "Pose"])
    df.to_csv(csv, index=False)
else:
    df = pd.read_csv(csv)
    


# Select device (MPS for Apple Silicon, otherwise CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Create model (force CPU mode)
model = SixDRepNet(gpu_id=-1)  # Ensure CUDA is not used

# Load images from file
file_path = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/misty-sidekick/headposeimagetest/processed_head/heads/"
image_files = os.listdir(file_path)

#remove any non-image files [.png, .jpg, .jpeg]
image_files = [file for file in image_files if file.endswith(('.png', '.jpg', '.jpeg'))]

for image_file in image_files:
    image_path = os.path.join(file_path, image_file)
    frame = cv2.imread(image_path)

    # Check if the image is loaded correctly
    if frame is None:
        raise IOError(f"Cannot open image file: {image_path}")

    # Rotate the image by 90 degrees
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Predict head pose
    pitch, yaw, roll = model.predict(frame_rgb)
    
    # Classify head pose
    pose_label = classify_head_pose(yaw, pitch)

    # Save the head pose data to the CSV file
    filename = os.path.basename(image_path)
    new_row = pd.DataFrame([{"Filename": filename, "Yaw": yaw[0], "Pitch": pitch[0], "Roll": roll[0], "Pose": pose_label}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv, index=False)

    # Draw the axis at the center of the image
    h, w, _ = frame.shape
    face_center = (w // 2, h // 2)
    model.draw_axis(frame, yaw, pitch, roll)

    # Save the image with the pose overlay
    image_name = os.path.basename(image_path)
    output_path = os.path.join(output_folder, image_name[:-4] + "_poseaxis.png")

    cv2.imwrite(output_path, frame)
    
    print(f"Image saved to: {output_path}")


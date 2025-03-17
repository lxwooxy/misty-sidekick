import cv2
import torch
from sixdrepnet import SixDRepNet
import numpy as np

# Select device (MPS for Apple Silicon, otherwise CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Create model (force CPU mode)
model = SixDRepNet(gpu_id=-1)  # Ensure CUDA is not used

# Load an image
image_path = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/Misty-Python-SDK/imagetest/processed_head/heads/group_20250304_160148_head_0.png"
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

# Function to classify head pose
def classify_head_pose(yaw, pitch):
    if abs(yaw) < 15:
        return "Facing Center"
    elif yaw < -15:
        return "Facing Right"
    elif yaw > 15:
        return "Facing Left"
    elif pitch > 20:
        return "Facing Away"
    return "Unknown"

# Classify head pose
pose_label = classify_head_pose(yaw, pitch)

# Draw the axis at the center of the image
h, w, _ = frame.shape
face_center = (w // 2, h // 2)
model.draw_axis(frame, yaw, pitch, roll)

# Display classification label
cv2.putText(frame, f"Pose: {pose_label}", (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

# Display the image with the pose overlay
cv2.imshow("Image - Head Pose Estimation", frame)

# Wait for a key press and close window
cv2.waitKey(0)
cv2.destroyAllWindows()
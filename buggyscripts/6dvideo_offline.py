import cv2
import torch
from sixdrepnet import SixDRepNet
import numpy as np

# Select device (MPS for Apple Silicon, otherwise CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Create model (force CPU mode)
model = SixDRepNet(gpu_id=-1)  # Ensure CUDA is not used

# Initialize video capture for pre-recorded video
video_path = "test.mp4"
cap = cv2.VideoCapture(video_path)

# Check if the video file is opened correctly
if not cap.isOpened():
    raise IOError(f"Cannot open video file: {video_path}")

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

# Process frames from the video
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video instead of stopping
        continue

    # Convert the frame to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Predict head pose
    pitch, yaw, roll = model.predict(frame_rgb)

    # Classify head pose
    pose_label = classify_head_pose(yaw, pitch)

    # Detect face center (Assuming face detection method is embedded in the model or external face detector)
    h, w, _ = frame.shape
    face_center = (w // 2, h // 2)  # Assuming center of frame for simplicity

    # Draw the axis at the detected face center
    model.draw_axis(frame, yaw, pitch, roll, face_center)

    # Display classification label
    cv2.putText(frame, f"Pose: {pose_label}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # Display the frame with the pose overlay
    cv2.imshow("Video - Head Pose Estimation", frame)

    # Exit on pressing the ESC key
    if cv2.waitKey(1) & 0xFF == 27:  # ASCII for ESC key
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

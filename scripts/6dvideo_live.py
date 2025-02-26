import cv2
import torch
from sixdrepnet import SixDRepNet

# Select device (MPS for Apple Silicon, otherwise CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Create model (force CPU mode)
model = SixDRepNet(gpu_id=-1)  # Ensure CUDA is not used

# Initialize webcam (use ID 0 for the default webcam)
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

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

# Start webcam feed and process frames
try:
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Predict head pose
        pitch, yaw, roll = model.predict(frame_rgb)

        # Classify head pose
        pose_label = classify_head_pose(yaw, pitch)

        # Draw the axis on the frame
        model.draw_axis(frame, yaw, pitch, roll)

        # Display classification label
        cv2.putText(frame, f"Pose: {pose_label}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Display the frame with the pose overlay
        cv2.imshow("Webcam - Head Pose Estimation", frame)

        # Exit on pressing the ESC key
        if cv2.waitKey(1) & 0xFF == 27:  # ASCII for ESC key
            break
finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

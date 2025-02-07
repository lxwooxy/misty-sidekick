import cv2
import numpy as np
from ultralytics import YOLO
from sklearn.cluster import DBSCAN

# Load YOLOv8 model pre-trained on COCO dataset
model = YOLO("yolov8m.pt")  # Use yolov8s.pt for speed, yolov8x.pt for best accuracy

# Open webcam
cap = cv2.VideoCapture(0)  # Use 0 for default webcam

if not cap.isOpened():
    raise IOError("Cannot open webcam")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO inference
    results = model(frame)

    # Extract bounding box heights and X positions for clustering
    bboxes = []
    features = []  # (x-center, height) used for clustering

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
            confidence = box.conf[0].item()  # Confidence score
            
            # Only keep high-confidence detections (90% or more)
            if confidence < 0.9:  
                continue

            # Compute height and X center (proxy for depth + spatial distance)
            height = y2 - y1
            x_center = (x1 + x2) // 2
            features.append([x_center, height])
            bboxes.append((x1, y1, x2, y2, confidence))

    # Convert to NumPy array for clustering
    if features:
        features = np.array(features)

        # Apply DBSCAN Clustering with eps=150 
        dbscan = DBSCAN(eps=150, min_samples=1).fit(features)  
        cluster_labels = dbscan.labels_  # -1 means noise (not in a cluster)
    else:
        cluster_labels = []

    # Define colors for clusters
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0), (128, 0, 128)]  # Green, Blue, Red, Orange, Purple

    # Draw bounding boxes with different colors based on cluster
    for i, (x1, y1, x2, y2, confidence) in enumerate(bboxes):
        group_id = cluster_labels[i] + 1  # Make labels "Group 1, 2, 3..."
        if cluster_labels[i] == -1:
            color = (0, 0, 0)  # Black for outliers
            group_text = "Isolated"
        else:
            color = colors[cluster_labels[i] % len(colors)]  
            group_text = f"Group {group_id}"

        label = f"Person: {confidence:.2f}"

        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Add group label (e.g., "Group 1") above the person
        cv2.putText(frame, group_text, (x1, y1 - 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Display confidence score below the group label
        cv2.putText(frame, label, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # Show updated frame
    cv2.imshow("Real-Time Person Grouping (Confidence ≥ 60%)", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()

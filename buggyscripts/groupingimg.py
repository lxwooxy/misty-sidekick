import cv2
import numpy as np
from ultralytics import YOLO
from sklearn.cluster import DBSCAN

# Load YOLOv8 model pre-trained on COCO dataset
model = YOLO("yolov8m.pt")  # Use yolov8s.pt for speed, yolov8x.pt for best accuracy

# Load image
image_path = "Misty-Python-SDK/images/coffee1.png"
img = cv2.imread(image_path)

# Run YOLO inference
results = model(img)

# Extract bounding box heights and X positions for clustering
bboxes = []
features = []  # (x-center, height) used for clustering

for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # Bounding box coordinates
        confidence = box.conf[0].item()  # Confidence score
        
        # Only keep high-confidence detections (50% or more)
        if confidence < 0.8:  
            continue
        
        # Only keep people (class label 0)
        if int(box.get_label()) != 0:
            continue

        # Compute height and X center (proxy for depth + spatial distance)
        height = y2 - y1
        x_center = (x1 + x2) // 2
        features.append([x_center, height])
        bboxes.append((x1, y1, x2, y2, confidence))

# Convert to NumPy array for clustering
features = np.array(features)

# Apply DBSCAN Clustering with eps=150 for looser grouping
#eps stands for epsilon, which is the maximum distance between two samples for one to be considered as in the neighborhood of the other.
#DBSCAN is a clustering algorithm that groups together points that are closely packed together (points with many nearby neighbors), marking as outliers points that are in low-density regions (whose nearest neighbors are too far away).
dbscan = DBSCAN(eps=170, min_samples=1).fit(features)  

cluster_labels = dbscan.labels_  # -1 means noise (not in a cluster)

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
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

    # Add group label (e.g., "Group 1") above the person
    cv2.putText(img, group_text, (x1, y1 - 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    # Display confidence score below the group label
    cv2.putText(img, label, (x1, y1 - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# Display the image and wait for a key press to close the window
cv2.imshow("Final DBSCAN Grouping (eps=150, Confidence 50%+)", img)
#save the image
filename = image_path.split("/")[-1][:-4]
cv2.imwrite(f"{filename}_DBSCAN.png", img)
#DBSCAN stands for Density-Based Spatial Clustering of Applications with Noise
cv2.setWindowProperty("Final DBSCAN Grouping (eps=150, Confidence 50%+)", cv2.WND_PROP_TOPMOST, 1)
cv2.waitKey(0)
cv2.destroyAllWindows()

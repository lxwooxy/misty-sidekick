import cv2
import numpy as np
from ultralytics import YOLO

def apply_static_noise(image, mask):
    """Apply TV static effect inside the given mask."""
    noise = np.random.randint(0, 256, image.shape, dtype=np.uint8)  # Create random noise
    return np.where(mask[..., None] == 255, noise, image)  # Apply noise only inside mask

# Load YOLOv8 segmentation model
model = YOLO("yolov8n-seg.pt")

# Load the image
image = cv2.imread("lola_1.jpg")

# Run YOLOv8 to detect and segment people
results = model(image)

# Extract the first detected person's mask
for result in results:
    for i, mask in enumerate(result.masks.xy):
        if int(result.boxes.cls[i]) == 0:  # 'person' class
            mask = np.array(mask, dtype=np.int32)

            # Create a blank mask
            mask_img = np.zeros(image.shape[:2], dtype=np.uint8)

            # Fill mask where person is detected
            cv2.fillPoly(mask_img, [mask], 255)

            # Apply static noise effect
            image = apply_static_noise(image, mask_img)

            break  # Only process the first detected person

# Save and display
cv2.imwrite("static_blurred_person.jpg", image)
cv2.imshow("Static Blurred Person", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

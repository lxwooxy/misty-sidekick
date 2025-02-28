import cv2
import numpy as np
from ultralytics import YOLO

def pixelate_region(image, mask, pixel_size=20):
    """Apply pixelation effect inside the given mask."""
    # Find bounding box of the mask
    x, y, w, h = cv2.boundingRect(mask)

    # Extract the region to pixelate
    roi = image[y:y+h, x:x+w]

    # Resize down and back up to create the pixelation effect
    small = cv2.resize(roi, (w // pixel_size, h // pixel_size), interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    # Apply only to the masked area
    mask_expanded = mask[y:y+h, x:x+w, None]  # Expand dims for broadcasting
    image[y:y+h, x:x+w] = np.where(mask_expanded == 255, pixelated, roi)

# Load the YOLOv8 segmentation model
model = YOLO("yolov8n-seg.pt")

# Load the image
image = cv2.imread("person.jpg")

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

            # Apply pixelation effect
            pixelate_region(image, mask_img, pixel_size=20)

            break  # Only process the first detected person

# Save and display
cv2.imwrite("pixelated_person.jpg", image)
cv2.imshow("Pixelated Person", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

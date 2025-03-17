import cv2
import numpy as np
import os
from ultralytics import YOLO


def apply_static_noise(image, mask):
    """Apply TV static effect inside the given mask."""
    noise = np.random.randint(0, 256, image.shape, dtype=np.uint8)  # Create random noise
    return np.where(mask[..., None] == 255, noise, image)  # Apply noise only inside mask

# Load YOLOv8 segmentation model
model = YOLO("yolov8x-seg.pt")

# Directory containing images
image_dir = "/Users/georginawoo/Desktop/HUNTER/TIER/MISTY/covfefe/Assets/images3"
output_dir = os.path.join(image_dir, "processed")
os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

# Process each image in the directory
for filename in os.listdir(image_dir):
    if filename.lower().endswith((".jpg", ".png", ".jpeg")):
        image_path = os.path.join(image_dir, filename)
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Skipping {filename}, could not read image.")
            continue

        # Run YOLOv8 to detect and segment people
        results = model(image, conf=0.5)
                
        # Apply static noise to all detected people
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

        # Save the processed image
        output_path = os.path.join(output_dir, filename)
        cv2.imwrite(output_path, image)
        print(f"Processed and saved: {output_path}")

print("Processing complete.")
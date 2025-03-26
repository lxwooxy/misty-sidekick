# Import libraries
import cv2
import numpy as np
import torch
from sixdrepnet import SixDRepNet
from ultralytics import YOLO

# Select device (MPS for Apple Silicon, otherwise CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Load SixDRepNet model (force CPU mode)
model = SixDRepNet(gpu_id=-1)

# Load YOLOv8 segmentation model
yolo_model = YOLO("yolov8n-seg.pt")  # Segmentation model

# Function to apply TV static to the detected person
def apply_static_noise(image, mask):
    """Apply TV static effect inside the given mask."""
    noise = np.random.randint(0, 256, image.shape, dtype=np.uint8)  # Generate static noise
    return np.where(mask[..., None] == 255, noise, image)  # Apply noise only inside mask

# List of names (files to process)
names = ["lola", "shankar"]

for name in names:
    for i in range(1, 6):
        img = cv2.imread(f'{name}_{i}.jpg')

        if img is None:
            print(f"Error loading {name}_{i}.jpg")
            continue

        # Step 1: Run SixDRepNet on the original image
        pitch, yaw, roll = model.predict(img.copy())  # Use a copy to keep original

        # Step 2: Detect person using YOLO segmentation
        results = yolo_model(img)

        # Create a blank mask
        mask_img = np.zeros(img.shape[:2], dtype=np.uint8)

        # Step 3: Extract first detected person's mask
        for result in results:
            for j, mask in enumerate(result.masks.xy):
                if int(result.boxes.cls[j]) == 0:  # 'person' class
                    mask = np.array(mask, dtype=np.int32)

                    # Fill mask where the person is detected
                    cv2.fillPoly(mask_img, [mask], 255)

                    # Apply static noise
                    img = apply_static_noise(img, mask_img)
                    break  # Process only the first detected person

        # Step 4: Draw axis on the **censored** image
        model.draw_axis(img, yaw, pitch, roll, size=100)

        # Step 5: Save and show the censored image with axis
        output_path = f'{name}_{i}_axis_censored.jpg'
        cv2.imwrite(output_path, img)
        print(f"Saved {output_path}")

        cv2.imshow("Censored Image with Axis", img)
        cv2.waitKey(0)

    cv2.destroyAllWindows()

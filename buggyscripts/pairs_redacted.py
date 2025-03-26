import cv2
import numpy as np
import glob
import os
from datetime import datetime

# Names of persons (update as needed)
person1 = "redacted1"
person2 = "redacted2"

# Get all images for each person
images1_paths = sorted(glob.glob(f"{person1}_*_axis_censored.jpg"))
images2_paths = sorted(glob.glob(f"{person2}_*_axis_censored.jpg"))

# Ensure both persons have the same number of images
if len(images1_paths) != len(images2_paths):
    raise ValueError("Mismatch in number of images between persons!")

# Process images in pairs
for i, (img1_path, img2_path) in enumerate(zip(images1_paths, images2_paths), start=1):
    # Load images
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        print(f"Skipping pair {i} due to missing image.")
        continue

    # Resize to match smallest dimensions
    min_height = min(img1.shape[0], img2.shape[0])
    min_width = min(img1.shape[1], img2.shape[1])

    img1_resized = cv2.resize(img1, (min_width, min_height))
    img2_resized = cv2.resize(img2, (min_width, min_height))

    # Stack images side by side
    collage = np.hstack([img1_resized, img2_resized])

    # Save the collage with the required filename format
    output_filename = f"collage_pair_{i}.jpg"
    cv2.imwrite(output_filename, collage)
    print(f"Saved {output_filename}")

print("All collages created successfully.")

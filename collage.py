import cv2
import numpy as np
import glob
import os
from datetime import datetime

#names = ["charles", "katherine", "lola", "lolahat","riyuan","ryan","ryanmask","shankar"]

#names = ["jaime4k", "lola4k"]

# names = ["lola", "shankar"]

names = ["redacted"]

for name in names:

    # Get all images matching the pattern *_axis.jpg
    image_paths = sorted(glob.glob(f"{name}*_axis.jpg"))

    # Load images
    images = [cv2.imread(img) for img in image_paths if cv2.imread(img) is not None]

    if len(images) == 0:
        raise ValueError(f"No {name}*_axis.jpg images found")

    #if there are 10 images, then we have 2 rows and 5 columns
    if len(images) == 10:
        rows, cols = 2, 5
        images = [images[:5], images[5:]]
        
        # Resize images to the same dimensions
        min_height = min(img.shape[0] for img in images[0])
        min_width = min(img.shape[1] for img in images[0])
        images_resized = [[cv2.resize(img, (min_width, min_height)) for img in row] for row in images]
        
        # Arrange images into a grid
        collage = np.vstack([np.hstack(row) for row in images_resized])
        
    else:
        # Determine collage layout (1 row, 5 columns)
        rows, cols = 1, 5


        # Resize images to the same dimensions
        min_height = min(img.shape[0] for img in images)
        min_width = min(img.shape[1] for img in images)
        images_resized = [cv2.resize(img, (min_width, min_height)) for img in images]

        # Arrange images into a single row
        collage = np.hstack(images_resized)

    # Check if the file already exists
    output_filename = f"{name}_collage.jpg"
    if os.path.exists(output_filename):
        # Append the current date and time to the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{name}_collage_{timestamp}.jpg"
    # Save the collage
    cv2.imwrite(output_filename, collage)
    print(f"Collage saved as {output_filename}")


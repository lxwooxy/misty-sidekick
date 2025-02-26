import cv2
import numpy as np
import glob

# Get all images matching the pattern *_axis.jpg
image_paths = sorted(glob.glob("*_axis.jpg"))

# Load images
images = [cv2.imread(img) for img in image_paths if cv2.imread(img) is not None]

if len(images) == 0:
    raise ValueError("No *_axis.jpg images found")

# Determine collage layout (1 row, 5 columns)
rows, cols = 1, 5

# Ensure we have exactly 5 images
if len(images) < cols:
    raise ValueError("Not enough images to create a 1x5 collage")

# Resize images to the same dimensions
min_height = min(img.shape[0] for img in images)
min_width = min(img.shape[1] for img in images)
images_resized = [cv2.resize(img, (min_width, min_height)) for img in images]

# Arrange images into a single row
collage = np.hstack(images_resized)

# Save the collage
cv2.imwrite("collage.jpg", collage)
print("Saved collage.jpg")

# Display the collage
cv2.imshow("Collage", collage)
cv2.waitKey(0)
cv2.destroyAllWindows()

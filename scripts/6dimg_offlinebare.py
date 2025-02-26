# Import SixDRepNet
from sixdrepnet import SixDRepNet
import cv2
import torch

# Select device (MPS for Apple Silicon, otherwise CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Create model (force CPU mode)
model = SixDRepNet(gpu_id=-1)

for i in range(1, 6):
    img = cv2.imread(f'test_{i}.jpg')
    
    if img is None:
        print(f"Error loading test_{i}.jpg")
        continue
    
    pitch, yaw, roll = model.predict(img)
    model.draw_axis(img, yaw, pitch, roll)
    
    # Save the processed image
    output_path = f'test_{i}_axis.jpg'
    cv2.imwrite(output_path, img)
    print(f"Saved {output_path}")
    
    cv2.imshow("test_window", img)
    cv2.waitKey(0)
    
cv2.destroyAllWindows()

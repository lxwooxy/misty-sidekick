# Import SixDRepNet
from sixdrepnet import SixDRepNet
import cv2
import torch


# Select device (MPS for Apple Silicon, otherwise CPU)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# Create model (force CPU mode)
model = SixDRepNet(gpu_id=-1)

names = ["charles", "katherine", "lola", "lolahat","riyuan","ryan","ryanmask","shankar"]

for name in names:

    for i in range(1, 6):
        img = cv2.imread(f'{name}_{i}.jpg')
        
        if img is None:
            print(f"Error loading {name}_{i}.jpg")
            continue
        
        pitch, yaw, roll = model.predict(img)
        model.draw_axis(img, yaw, pitch, roll)
        
        # Save the processed image
        output_path = f'{name}_{i}_axis.jpg'
        cv2.imwrite(output_path, img)
        print(f"Saved {output_path}")
        
        # cv2.imshow("test_window", img)
        # cv2.waitKey(0)
        
    cv2.destroyAllWindows()

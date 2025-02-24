import os
import time
import base64
from dotenv import load_dotenv
from mistyPy.Robot import Robot

# Load environment variables
load_dotenv()

MISTY_IP = os.getenv("MISTY_IP")

if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

misty = Robot(MISTY_IP)

# Create a local folder for images
image_folder = "misty_frames"
os.makedirs(image_folder, exist_ok=True)

# Take 60 pictures per second for 5 seconds (total: 300 images)
frames_per_second = 60
duration_seconds = 5
total_frames = frames_per_second * duration_seconds

print("Starting capture...")

for i in range(total_frames):
    misty_filename = f"frame_{i:04d}.jpg"  # Saved in Misty's storage
    local_filename = os.path.join(image_folder, misty_filename)  # Saved locally

    # Take picture and store it on Misty
    response = misty.take_picture(base64=True, fileName=misty_filename, width=640, height=480)

    if response.status_code == 200:
        image_data = response.json().get("result", {}).get("base64")
        
        if image_data:
            # Decode and save locally
            with open(local_filename, "wb") as img_file:
                img_file.write(base64.b64decode(image_data))
            print(f"Saved {local_filename}")
        else:
            print(f"Warning: No base64 image data for frame {i}")
    else:
        print(f"Failed to capture frame {i}: {response.text}")

    time.sleep(1 / frames_per_second)  # Maintain 60 FPS

print("Capture complete!")

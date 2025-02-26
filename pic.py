import os
import base64
from dotenv import load_dotenv
from mistyPy.Robot import Robot
from datetime import datetime

name = "ryan"
# Load environment variables from .env file
load_dotenv()

MISTY_IP = os.getenv("MISTY_IP")

if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

misty = Robot(MISTY_IP)

# Take a picture
response = misty.take_picture(base64=True, fileName="test.jpg", width=4160, height=3120)

#use 3940x2160 for 4k
if response.status_code == 200:
    image_data = response.json().get("result", {}).get("base64")
    
    if image_data:
        # Decode the base64 image and save it as a file
        with open(f"{name}.jpg", "wb") as img_file:
            file_path = f"{name}.jpg"
            if os.path.exists(file_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"{name}_{timestamp}.jpg"

            with open(file_path, "wb") as img_file:
                img_file.write(base64.b64decode(image_data))
        print("Image saved as misty_image.jpg")
    else:
        print("No base64 image data received.")
else:
    print("Failed to take picture:", response.text)

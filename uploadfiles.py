import os
import sys
from mistyPy.Robot import Robot
from mistyPy.Events import Events
import time
import random
import requests



from dotenv import load_dotenv

# Load Misty's IP from environment variables
load_dotenv()
MISTY_IP = os.getenv("MISTY_IP")
if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

# Initialize Misty
misty = Robot(MISTY_IP)

# List of files: (filename, is_audio, is_video)
files = [
    ("domoarigato.wav", True, False),
    ("sound.wav", True, False),
    ("rickroll.mp4", False, True),
]

for filename, is_audio, is_video in files:
    with open(filename, "rb") as f:
        file_bytes = f.read()

    print(f"Uploading {filename}...")

    misty.upload(
        file_bytes,
        filename,
        file_type="audio" if is_audio else "video",
        overwrite=True
    )
import asyncio
import websockets
import cv2
import numpy as np
import time
import os
from dotenv import load_dotenv
from mistyPy.Robot import Robot

# Load environment variables from .env file
load_dotenv()

MISTY_IP = os.getenv("MISTY_IP")

if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

misty = Robot(MISTY_IP)

misty.start_recording_video("MyHomeVideo", "false", 60, 1920, 1080)

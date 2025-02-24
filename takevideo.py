import time
import os
from dotenv import load_dotenv
from mistyPy.Robot import Robot

# Load environment variables
load_dotenv()

MISTY_IP = os.getenv("MISTY_IP")

if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

misty = Robot(MISTY_IP)

# Video filename on Misty's storage
misty_video_filename = "MyHomeVideo"
local_video_filename = "MyHomeVideo.mp4"  # Save as .mp4 locally

# Start recording (5 seconds)
misty.start_recording_video(misty_video_filename, 5)

print("Recording video for 5 seconds...")
time.sleep(5)

# Stop recording
misty.stop_recording_video()

# Retrieve the list of recorded videos
video_list_response = misty.get_video_recordings_list()

if video_list_response.status_code == 200:
    video_list = video_list_response.json().get("result", [])
    
    if video_list:
        print("Videos stored on Misty:")
        for video in video_list:
            print("-", video)
    else:
        print("No videos found on Misty's storage.")
else:
    print(f"Failed to retrieve video list: {video_list_response.text}")

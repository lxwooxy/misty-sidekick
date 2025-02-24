import asyncio
import websockets
import cv2
import numpy as np
import time
from mistyPy.Robot import Robot

# Set Misty's IP
MISTY_IP = "YOUR_MISTY_IP"
VIDEO_PORT = 5678  # WebSocket port

# Initialize Misty
misty = Robot(MISTY_IP)

# Video settings
frames_per_second = 30  # Misty's actual streaming FPS
duration_seconds = 5  # Record for 5 seconds
frame_size = (640, 480)  # Video resolution
video_filename = "misty_video.mp4"

# Start Misty's video streaming
misty.start_video_streaming(VIDEO_PORT)
print("Misty video streaming started...")

async def record_video():
    uri = f"ws://{MISTY_IP}:{VIDEO_PORT}"
    async with websockets.connect(uri) as websocket:
        print("Connected to Misty's video stream")

        # OpenCV video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
        video_writer = cv2.VideoWriter(video_filename, fourcc, frames_per_second, frame_size)

        start_time = time.time()
        while time.time() - start_time < duration_seconds:
            try:
                frame_bytes = await websocket.recv()  # Get frame
                np_arr = np.frombuffer(frame_bytes, np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # Convert to OpenCV format

                if frame is not None:
                    video_writer.write(frame)  # Write frame to video
                    cv2.imshow("Misty Video Stream", frame)  # Show live video
                    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit early
                        break
                else:
                    print("Warning: Received empty frame")
            except Exception as e:
                print(f"Error receiving frame: {e}")

        video_writer.release()  # Save video file
        cv2.destroyAllWindows()  # Close video window

        print(f"Video saved as {video_filename}")

# Run video recording coroutine
asyncio.run(record_video())

# Stop Misty's video stream
misty.stop_video_streaming()
print("Misty video streaming stopped.")

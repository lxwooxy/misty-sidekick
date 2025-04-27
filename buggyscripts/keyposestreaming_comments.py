from mistyPy.Robot import Robot
from mistyPy.Events import Events
import time
import math
import random
import os
from dotenv import load_dotenv
import requests
import cv2
import numpy as np
import base64
import time
from ultralytics import YOLO

# Load YOLOv8 Pose model
model = YOLO("yolov8l-pose.pt")

def draw_yolo_pose(frame, result, confidence_threshold=0.7):
    """Draw YOLO pose skeleton with confidence filtering."""
    if result is None or result.keypoints is None:
        return frame

    HEAD_KEYPOINTS = [0, 1, 2, 3, 4] # Left eye, right eye, nose, left ear, right ear
    JOINTS = [7, 9, # Left elbow, left wrist
              8, 10, # Right elbow, right wrist
              13, 15, # Left knee, left ankle
              14, 16] # Right knee, right ankle
    
    
    # Defining the skeleton structure
    # Each tuple represents a pair of keypoints to connect with a line
    # For example, (5, 6) connects keypoint 5 to keypoint 6, which is the left shoulder to right shoulder
    skeleton = [
        (5, 6),   # Shoulders
        (5, 7), (7, 9),  # Left Arm: 5 to 7 (shoulder to elbow), 7 to 9 (elbow to wrist)
        (6, 8), (8, 10), # Right Arm: 6 to 8 (shoulder to elbow), 8 to 10 (elbow to wrist)
        (11, 12),        # Hips: 11 to 12 (left hip to right hip)
        (5, 11), (6, 12),# Torso: 5 to 11 (left shoulder to left hip), 6 to 12 (right shoulder to right hip)
        (11, 13), (13, 15), # Left Leg: 11 to 13 (left hip to left knee), 13 to 15 (left knee to left ankle)
        (12, 14), (14, 16)  # Right Leg: 12 to 14 (right hip to right knee), 14 to 16 (right knee to right ankle)
    ]

    for kp in result.keypoints.data:

        # kp is a numpy array of shape (17, 3) where each row is [x, y, confidence]
        # the 17 rows correspond to the 17 keypoints of the human pose
        # x and y are the coordinates of the keypoint, and confidence is the confidence score of the detection
        
        # Draw lines (only if both points are confident)
        for i, j in skeleton:
            
            if kp[i][2] > confidence_threshold and kp[j][2] > confidence_threshold:
                
                pt1 = (int(kp[i][0]), int(kp[i][1]))
                pt2 = (int(kp[j][0]), int(kp[j][1]))
                cv2.line(frame, pt1, pt2, (0, 255, 255), 2)

        # Draw keypoints
        for idx, (x, y, conf) in enumerate(kp):
            
            if conf < confidence_threshold:
                continue  # Skip low confidence keypoints

            if idx in HEAD_KEYPOINTS:
                color = (0, 255, 0)  # Green for eyes, nose, ears
            elif idx in JOINTS:
                color = (0, 0, 255)  # Red for elbows, wrists, knees, ankles
            else:
                color = (255, 0, 0)  # Blue for shoulders, hips

            cv2.circle(frame, (int(x), int(y)), 5, color, -1) # Draw keypoint with the specified color

    return frame



# Load Misty's IP from environment variables
load_dotenv()

MISTY_IP = os.getenv("MISTY_IP")
#MISTY_IP = os.getenv("MISTY_IP_2")

if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

# Initialize Misty
misty = Robot(MISTY_IP)
misty.change_led(0, 255, 0)
misty.display_image("e_DefaultContent.jpg")


# Variables
waving_now = False
person_width_history = [0, 0, 0, 0]
pose_estimation_running = False  # Track if pose estimation is running
person_lost_count = 0  # Track how many frames a person is missing
lost_threshold = 5  # Number of frames before stopping pose estimation
last_pose_keypoints = None



# Event handler for analyzing the human pose
last_wave_time = 0  # Track last time Misty waved

def human_pose(data):
    global waving_now, last_wave_time, last_pose_keypoints

    # If no person was detected recently, ignore pose data
    if not pose_estimation_running:
        return  # Stop processing this frame
    
    last_pose_keypoints = data["message"]["keypoints"]

    print("Starting pose estimation")

    keypoints = data["message"]["keypoints"]

    # Filter only high-confidence keypoints (confidence ≥ 0.6)
    valid_keypoints = [k for k in keypoints if confident(k)]

    if len(valid_keypoints) < 5:
        print(f"❌ Not enough valid keypoints ({len(valid_keypoints)}). Ignoring detection.")
        return  

    # Store fresh keypoints
    misty.last_pose_keypoints = keypoints
    #print("✅ Detected keypoints:", keypoints)

    # Prevent rapid wave retriggering
    current_time = time.time()
    if current_time - last_wave_time < 7:  # Add a delay before allowing another wave
        print("🕒 Too soon to wave again. Ignoring detection.")
        return
    

    if not waving_now:
        print("👋 Checking for waving motion...")
        if confident(keypoints[7]) and confident(keypoints[5]) and confident(keypoints[9]):
            print("✅ Left hand detected")
            print(f"Left Shoulder Y: {keypoints[5]['imageY']}, Elbow Y: {keypoints[7]['imageY']}, Wrist Y: {keypoints[9]['imageY']}")

            elbow_wrist_check = pair_correlation(keypoints[7], keypoints[5])
            wrist_above_elbow = pair_correlation(keypoints[5], keypoints[9])
            valid_scale = scale_valid(keypoints[7], keypoints[5])

            print(f"🔹 Elbow above Shoulder? {elbow_wrist_check}")
            print(f"🔹 Wrist above Elbow? {wrist_above_elbow}")
            print(f"🔹 Scale Valid? {valid_scale}")

            if elbow_wrist_check and wrist_above_elbow and valid_scale:
                print("✅ Left arm motion validated")
                waving_now = True
                last_wave_time = current_time  # Update last wave time
                wave_back("left")
        if confident(keypoints[8]) and confident(keypoints[6]) and confident(keypoints[10]):
            print("✅ Right hand detected")
            print(f"Right Shoulder Y: {keypoints[6]['imageY']}, Elbow Y: {keypoints[8]['imageY']}, Wrist Y: {keypoints[10]['imageY']}")
            elbow_wrist_check = pair_correlation(keypoints[8], keypoints[6])
            wrist_above_elbow = pair_correlation(keypoints[6], keypoints[10])
            valid_scale = scale_valid(keypoints[8], keypoints[6])
        
            print(f"🔹 Elbow above Shoulder? {elbow_wrist_check}")
            print(f"🔹 Wrist above Elbow? {wrist_above_elbow}")
            print(f"🔹 Scale Valid? {valid_scale}")
            
            if elbow_wrist_check and wrist_above_elbow and valid_scale:
                print("✅ Right arm motion validated")
                waving_now = True
                last_wave_time = current_time
                wave_back("right")

    

# Functions helper for the human pose, scale valid checks if the distance between two keypoints is greater than 60 pixels
def scale_valid(keypoint_one, keypoint_two):
    x_offset = keypoint_one["imageX"] - keypoint_two["imageX"]
    y_offset = keypoint_one["imageY"] - keypoint_two["imageY"]
    return math.sqrt(x_offset**2 + y_offset**2) > 60

def confident(data):
    return data["confidence"] >= 0.6

def pair_correlation(keypoint_one, keypoint_two):
    return keypoint_one["imageY"] > keypoint_two["imageY"]

def wave_back(arm):
    global waving_now

    # If pose estimation is not running, don't wave
    if not pose_estimation_running:
        #print("❌ No person detected. Ignoring wave.")
        waving_now = False
        return  

    if arm == "left":
        print("Waving back left")
        misty.play_audio("s_Acceptance.wav")
        misty.display_image("e_Joy2.jpg")
        misty.transition_led(0, 90, 0, 0, 255, 0, "Breathe", 800)
        misty.move_arms(80, -89)
        time.sleep(1)
        misty.move_arms(80, 0)
        time.sleep(0.75)
        misty.move_arms(80, -89)
        time.sleep(0.75)
    else:
        print("Waving back right")
        misty.play_audio("s_Awe.wav")
        misty.display_image("e_Love.jpg")
        misty.transition_led(90, 0, 0, 255, 0, 0, "Breathe", 800)
        misty.move_arms(-89, 80)
        time.sleep(1)
        misty.move_arms(0, 80)
        time.sleep(0.75)
        misty.move_arms(-89, 80)
        time.sleep(0.75)

    time.sleep(1.5)
    misty.display_image("e_DefaultContent.jpg")
    misty.transition_led(0, 40, 90, 0, 130, 255, "Breathe", 1200)
    misty.move_arms(random.randint(70, 89), random.randint(70, 89))
    time.sleep(1.5)

    # print("Cooldown started... Misty will not respond for 5 seconds.")
    # time.sleep(5)
    waving_now = False



# Human pose estimation event
def start_human_pose_estimation():
    global pose_estimation_running
    if not pose_estimation_running:
        print("🚀 Starting Pose Estimation")
        misty.stop_pose_estimation()  # Ensure we stop before restarting
        misty.start_pose_estimation(0.2, 0, 1)

        # Only register the event if it is not already registered
        try:
            misty.register_event(event_name="pose_estimation", event_type=Events.PoseEstimation, keep_alive=True, callback_function=human_pose)
        except Exception as e:
            print(f"⚠️ Pose estimation event already registered: {e}")

        pose_estimation_running = True  # Set flag to indicate pose estimation is running

def person_detection(data):
    global waving_now, pose_estimation_running, person_lost_count

    if data["message"]["confidence"] >= 0.75:
        #print("✅ Person detected")
        person_lost_count = 0  # Reset lost count
        width_of_human = data["message"]["imageLocationRight"] - data["message"]["imageLocationLeft"]
        person_width_history.pop(0)
        person_width_history.append(width_of_human)
        start_human_pose_estimation()
    else:
        person_lost_count += 1
        if person_lost_count >= lost_threshold:
            #print("❌ No person detected for multiple frames. Stopping pose estimation.")
            misty.last_pose_keypoints = []  # Clear stored keypoints
            waving_now = False  # Prevent Misty from responding

            if pose_estimation_running:
                misty.stop_pose_estimation()
                pose_estimation_running = False  # Reset flag to indicate pose estimation is stopped
            person_lost_count = 0  # Reset lost counter


# Person tracking event
def start_person_tracking():
    misty.start_object_detector(0.5, 0, 15)
    misty.register_event(event_name="person_detection", event_type=Events.ObjectDetection, callback_function=person_detection, keep_alive=True)



last_touch_time = 0  # Track last head touch time

last_touch_time = 0  # Track last head touch time
processing_touch = False  # Track if Misty is already reacting

def head_touched(data):
    """Plays a sound and changes Misty's expression when touched, then resets after 2 seconds."""
    global last_touch_time, processing_touch

    message = data["message"]
    current_time = time.time()

    # If Misty is already reacting to a touch, ignore new touches
    if processing_touch:
        return

    # Prevent rapid retriggers within 1 second
    if current_time - last_touch_time < 3:
        return
    last_touch_time = current_time  # Update last touch time
    processing_touch = True  # Lock the event handler

    # Check if the head is touched
    if message["isContacted"] and message["sensorId"] == "cap":
        sensor_position = message["sensorPosition"]
        print(f"🎵 Misty's head ({sensor_position}) was touched!")

        if sensor_position in ["HeadFront", "HeadBack"]:
            misty.play_audio("s_Love.wav")  
            misty.speak("Hel")
            #misty.play_audio("sound.wav")  
            misty.display_image("e_Love.jpg")
            misty.move_arms(-90, -90)

        elif sensor_position == "Scruff":
            misty.play_audio("sound.wav")  
            misty.display_image("e_EcstacyStarryEyed.jpg")

            dance_duration = 10  # seconds
            interval = 0.6
            start_time = time.time()

            rgb_colors = [
                {"red": 255, "green": 0, "blue": 0},     # Red
                {"red": 0, "green": 255, "blue": 0},     # Green
                {"red": 0, "green": 0, "blue": 255},     # Blue
                {"red": 255, "green": 255, "blue": 0},   # Yellow
                {"red": 0, "green": 255, "blue": 255},   # Cyan
                {"red": 255, "green": 0, "blue": 255},   # Magenta
                {"red": 255, "green": 255, "blue": 255}, # White
            ]
            color_index = 0

            while time.time() - start_time < dance_duration:
                # Tilt head left or right randomly
                tilt = random.choice([-20, 20])
                misty.move_head(0, tilt, 0, 70)

                # Move arms randomly within safe range
                left_arm = random.randint(-90, 90)
                right_arm = random.randint(-90, 90)
                misty.move_arms(left_arm, right_arm)

                # Change chest LED color
                color = rgb_colors[color_index % len(rgb_colors)]
                misty.change_led(color["red"], color["green"], color["blue"])
                color_index += 1

                time.sleep(interval)

            # Reset pose and LED
            misty.move_head(0, 0, 0, 70)
            misty.move_arms(0, 0)
            misty.change_led(0, 0, 0)


        elif sensor_position == "HeadRight":
            misty.play_audio("s_Awe.wav")
            misty.display_image("e_Admiration.jpg")
            misty.move_head(-20, 20, -10)  # Look up and to the right
 

        elif sensor_position == "HeadLeft":
            misty.play_audio("s_Joy.wav")
            misty.display_image("e_Joy.jpg")
            misty.move_head(-20, 20, 10)  # Look up and to the right

        
        elif sensor_position == "Chin":
            misty.play_audio("s_Joy2.wav")
            misty.display_image("e_Amazement.jpg")
            misty.move_head(-10, 0, 0)  # Look up and to the left


        # Wait 2 seconds before resetting Misty to normal
        time.sleep(2)
        misty.display_image("e_DefaultContent.jpg")  # Reset face
        
        misty.move_head(0, 0, 0)  # Reset head position
        
        misty.move_arms(90,90)
        misty.stop_audio()
        time.sleep(1)

    processing_touch = False  # Unlock the event handler

# Register TouchSensor event
misty.register_event(
    event_name="head_touch",
    event_type=Events.TouchSensor,
    callback_function=head_touched,
    keep_alive=True
)

def snapshot_stream_with_yolo():
    while True:
        response = misty.take_picture(base64=True, width=640, height=480)

        if response.status_code == 200: # 200 == success! 
            
            image_data = response.json().get("result", {}).get("base64")
            if image_data:
                img_bytes = base64.b64decode(image_data)
                np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
                frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if frame is not None:
                    # ---- YOLO Pose Estimation ----
                    # Returns a list of results, - each result corresponds to a detected person
                    results = model(frame)

                    # For each person detected, draw the pose skeleton 
                    for result in results:
                        frame = draw_yolo_pose(frame, result)



# Start program
snapshot_stream_with_yolo()

#start_person_tracking()
misty.keep_alive()

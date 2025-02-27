from mistyPy.Robot import Robot
from mistyPy.Events import Events
import time
import math
import random
import os
from dotenv import load_dotenv

# Load Misty's IP from environment variables
load_dotenv()
MISTY_IP = os.getenv("MISTY_IP")
if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

# Initialize Misty
misty = Robot(MISTY_IP)
misty.change_led(0, 255, 0)
misty.display_image("e_DefaultContent.jpg")

# Variables
waving_now = False
person_width_history = [0, 0, 0, 0]

# Event handler for analyzing the human pose
def human_pose(data):
    global waving_now
    print("Starting pose estimation")
    
    keypoints = data["message"]["keypoints"]
    print("Detected keypoints:", keypoints)

    if not waving_now:
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
                wave_back("left")
    

# Functions helper for the human pose
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

    # Cooldown before detecting another wave
    print("Cooldown started... Misty will not respond for 5 seconds.")
    time.sleep(5)  # Wait 5 seconds before allowing a new wave detection
    waving_now = False


# Human pose estimation event
def start_human_pose_estimation():
    misty.start_pose_estimation(0.2, 0, 1)
    misty.register_event(event_name="pose_estimation", event_type=Events.PoseEstimation, keep_alive=True, callback_function=human_pose)

# Event handler for analyzing person detection
def person_detection(data):
    if data["message"]["confidence"] >= 0.6:
        print("person detected")
        
        width_of_human = data["message"]["imageLocationRight"] - data["message"]["imageLocationLeft"]
        person_width_history.pop(0)
        person_width_history.append(width_of_human)

# Person tracking event
def start_person_tracking():
    misty.start_object_detector(0.5, 0, 15)
    misty.register_event(event_name="person_detection", event_type=Events.ObjectDetection, callback_function=person_detection, keep_alive=True)

# Start program
start_person_tracking()
start_human_pose_estimation()
misty.keep_alive()

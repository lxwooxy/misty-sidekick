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
misty.move_head(0, 0, 0)
misty.display_image("e_DefaultContent.jpg")

# Constants
yaw_left = 81.36
yaw_right = -85.37
pitch_up = -40.10
pitch_down = 26.92

# Variables
curr_head_pitch = 0
curr_head_yaw = 0
waving_now = False
person_width_history = [0, 0, 0, 0]

#Event handler for getting the current head position
def curr_position(data):
    global curr_head_pitch, curr_head_yaw
    if data["message"]["sensorId"] == "ahp":
        curr_head_pitch = data["message"]["value"]
    if data["message"]["sensorId"] == "ahy":
        curr_head_yaw = data["message"]["value"]

def get_pos():
    misty.register_event(event_name="get_curr_position", event_type= Events.ActuatorPosition, keep_alive= True, callback_function=curr_position)
    time.sleep(0.25)
    misty.unregister_event(event_name="get_curr_position")

#Event handler for analyzing the human pose
def human_pose(data):
    global waving_now
    print("starting pose estimation")
    #print("Keypoints detected:", data["message"]["keypoints"])
    
    keypoints = data["message"]["keypoints"]
    
    # 5,6- Shoulder 7,8- Elbow  9,10- Wrist 

    if (waving_now == False):
        #left hand
        if (confident(keypoints[7]) and confident(keypoints[5]) and confident(keypoints[9])):
            if (pair_correlation(keypoints[7],keypoints[5]) and pair_correlation(keypoints[5],keypoints[9])):
                if (scale_valid(keypoints[7],keypoints[5])):
                    waving_now = True
                    wave_back("left")
                    
        #right hand
        elif (confident(keypoints[8]) and confident(keypoints[6]) and confident(keypoints[10])):
            if (pair_correlation(keypoints[8],keypoints[6]) and pair_correlation(keypoints[6],keypoints[10])):
                if (scale_valid(keypoints[8],keypoints[6])):
                    waving_now = True
                    wave_back("right")       

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
    else :
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
    waving_now = False

# Human pose estimation event
def start_human_pose_estimation():
    misty.start_pose_estimation(0.2, 0, 1)
    misty.register_event(event_name="pose_estimation", event_type=Events.PoseEstimation, keep_alive= True, callback_function= human_pose)

#Event handler for analyzing person detection
def person_detection(data):
    if data["message"]["confidence"] >= 0.6:
        print("person detected")
        
        width_of_human = data["message"]["imageLocationRight"] - data["message"]["imageLocationLeft"]
        person_width_history.pop(0)
        person_width_history.append(width_of_human)
        
        # The first part checks if this measurement is the closest person and the second part checks if there is only one person that Misty can see
        if abs(width_of_human - min(person_width_history)) > abs(width_of_human - max(person_width_history)) or std_deviation(person_width_history) <= 40:
            x_error = (160.0 - (data["message"]["imageLocationLeft"] + data["message"]["imageLocationRight"]) / 2.0) / 160.0
            y_error = (160.0 - 1.4 * data["message"]["imageLocationTop"] + 0.2 * data["message"]["imageLocationBottom"]) / 160.0
            threshold = max(0.1, (341.0 - width_of_human) / 1000.0)

            get_pos()
            actuate_to_yaw = curr_head_yaw + x_error * ((yaw_left - yaw_right) / 6.0) if abs(x_error) > threshold else None
            actuate_to_pitch = curr_head_pitch - y_error * ((pitch_down - pitch_up) / 3.0) if abs(y_error) > threshold else None
        
            if abs(curr_head_pitch - round(actuate_to_pitch)) > 11 or abs(curr_head_yaw - round(actuate_to_yaw)) > 11:
                misty.move_head(actuate_to_pitch, None, actuate_to_yaw)

# Functions helper for person detection
def std_deviation(array):
    mean_value = sum(array) / len(array)
    return math.sqrt(sum([(x - mean_value) ** 2 for x in array]) / len(array))

# Person tracking event
def start_person_tracking() :
    misty.start_object_detector(0.5, 0, 15)
    misty.register_event(event_name="person_detection", event_type= Events.ObjectDetection, callback_function=person_detection, keep_alive=True)

# Start program
start_person_tracking()
start_human_pose_estimation()
misty.keep_alive()
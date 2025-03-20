from mistyPy.Robot import Robot
from mistyPy.Events import Events
import os
from dotenv import load_dotenv
import time

# Load Misty's IP from environment variables
load_dotenv()
MISTY_IP = os.getenv("MISTY_IP")
if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

# Initialize Misty
misty = Robot(MISTY_IP)
misty.change_led(0, 255, 0)
misty.display_image("e_DefaultContent.jpg")

def face_recognition(data):
    """ Check if Misty recognizes Georgina. """
    
    #print(data)
    face_name = data["message"].get("personName", "")

    if face_name == "Georgina":
        print(f"✅ Recognized Georgina! ")
        
        # Misty reacts
        misty.display_image("e_Joy.jpg")  # Show happy face
        misty.change_led(0, 255, 255)  # Change LED color
        misty.speak("Hi, Georgina!")  # Say hi

        # Reset Misty’s face and LED after 3 seconds
        time.sleep(3)
        misty.display_image("e_DefaultContent.jpg")
        misty.change_led(0, 255, 0)
    else:
        print(f"❌ Face detected, but not Georgina (Detected: {face_name})")


def start_face_tracking():
    """ Start face recognition. """
    misty.start_face_recognition()
    misty.register_event(
        event_name="face_recognition",
        event_type=Events.FaceRecognition,
        callback_function=face_recognition,
        keep_alive=True
    )

# Start program
start_face_tracking()


start_face_tracking()
misty.keep_alive()

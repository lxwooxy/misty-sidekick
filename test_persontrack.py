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

face_recognition_active = False  # Track whether face recognition is running

def face_recognition(data):
    """ Check if Misty recognizes Georgina and stop recognition after greeting. """
    global face_recognition_active

    if not face_recognition_active:
        return  # Ignore event if recognition is already deactivated

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

        # Stop face recognition and unregister event
        misty.stop_face_recognition()
        misty.unregister_event("face_recognition")  # Unregister event so it doesn't trigger again
        face_recognition_active = False
        print("🔴 Stopped and unregistered face recognition.")

        # Restart keyphrase recognition
        restart_listening()

    else:
        print(f"❌ Face detected, but not Georgina (Detected: {face_name})")
        
        # Misty reacts
        misty.display_image("e_Joy.jpg")  # Show happy face
        misty.change_led(0, 255, 255)  # Change LED color
        misty.speak("Hi there!")  # Say hi

        # Reset Misty’s face and LED after 3 seconds
        time.sleep(3)
        misty.display_image("e_DefaultContent.jpg")
        misty.change_led(0, 255, 0)

        # Stop face recognition and unregister event
        misty.stop_face_recognition()
        misty.unregister_event("face_recognition")  # Unregister event so it doesn't trigger again
        face_recognition_active = False
        print("🔴 Stopped and unregistered face recognition.")

        # Restart keyphrase recognition
        restart_listening()
        

def start_face_tracking():
    """ Start face recognition. """
    global face_recognition_active

    if not face_recognition_active:
        print("🚀 Starting Face Recognition...")
        misty.start_face_recognition()
        misty.register_event(
            event_name="face_recognition",
            event_type=Events.FaceRecognition,
            callback_function=face_recognition,
            keep_alive=False  # Set to False so it doesn't persist forever
        )
        face_recognition_active = True

def keyphrase_detected(data):
    """ Debug Misty's keyphrase recognition by printing raw data. """
    print(f"🔊 Keyphrase Event Data: {data}")  # Print raw event data

    print("🗣️ Heard 'Hey Misty'! Starting face recognition...")
    start_face_tracking()



def start_listening():
    """ Start keyphrase recognition for 'Hey Misty'. """
    print("👂 Starting keyphrase recognition...")
    response = misty.start_key_phrase_recognition()

    print(f"🔧 start_key_phrase_recognition() Response: {response.json()}")  # Debug response

    misty.register_event(
        event_name="keyphrase",
        event_type=Events.KeyPhraseRecognized,
        callback_function=keyphrase_detected,
        keep_alive=True
    )


def restart_listening():
    """ Fully reset Misty's ASR and restart keyphrase recognition. """
    print("🔄 Restarting keyphrase recognition (with audio service reset)...")

    try:
        misty.unregister_event("keyphrase")
    except:
        print("⚠️ Tried to unregister keyphrase event, but it may not have been registered.")

    # Stop keyphrase recognition (just in case it's still running)
    misty.stop_key_phrase_recognition()
    time.sleep(0.5)
    
    # Reset the audio service to avoid needing a robot reboot
    misty.stop_audio_service()
    time.sleep(2)
    misty.start_audio_service()
    time.sleep(2)

    start_listening()


# Start program
start_listening()
misty.keep_alive()

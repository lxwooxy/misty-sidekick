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

import random

def wave_back():
    armoptions = ["left", "right", "fitness", "bee"]
    
    randarm = random.randint(0,3)
    
    arm = armoptions[randarm]
    
    if arm == "left":
        print("Waving back left")
        #misty.play_audio("s_Acceptance.wav")
        misty.speak("Hey, human!")
        misty.display_image("e_Joy2.jpg")
        misty.transition_led(0, 90, 0, 0, 255, 0, "Breathe", 800)
        misty.move_arms(80, -89)
        time.sleep(1)
        misty.move_arms(80, 0)
        time.sleep(0.75)
        misty.move_arms(80, -89)
        time.sleep(0.75)
    elif arm == "right":
        print("Waving back right")
        #misty.play_audio("s_Awe.wav")
        misty.speak("Hello there!")
        misty.display_image("e_Love.jpg")
        misty.transition_led(90, 0, 0, 255, 0, 0, "Breathe", 800)
        misty.move_arms(-89, 80)
        time.sleep(1)
        misty.move_arms(0, 80)
        time.sleep(0.75)
        misty.move_arms(-89, 80)
        time.sleep(0.75)
        
    elif arm == "fitness":
        print("The fitness")
        #misty.play_audio("s_Awe.wav")
        fitness = """The FitnessGram Pacer test is a multistage aerobic capacity test. Just kidding."""
        misty.speak(fitness)
        misty.display_image("e_Rage3.jpg")
        misty.transition_led(255, 0, 0, 0, 0, 0, "Breathe", 800)
        time.sleep(3)
    
    else:
        print("Bee movie")
        #misty.play_audio("s_Awe.wav")
        fitness = "According to all known laws of aviation, there is no way that a bee should be able to fly."
        misty.speak(fitness)
        misty.display_image("e_Joy2.jpg")
        misty.transition_led(255, 255, 0, 0, 0, 0, "Breathe", 800)
        time.sleep(3)


    time.sleep(1)
    misty.display_image("e_DefaultContent.jpg")
    misty.transition_led(0, 40, 90, 0, 130, 255, "Breathe", 1200)
    misty.move_arms(random.randint(70, 89), random.randint(70, 89))

    #print("calling start listening at the end of wave back")
    #start_listening()
    restart_listening()


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

    #print("🗣️ Heard 'Hey Misty'! Starting face recognition...")
    wave_back()


def start_listening():
    """ Start keyphrase recognition for 'Hey Misty'. """
    print("start listening called ")
    misty.stop_key_phrase_recognition()
    print("stop keyphrase called ")
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

    # try:
    #     misty.unregister_event("keyphrase")
    # except:
    #     print("⚠️ Tried to unregister keyphrase event, but it may not have been registered.")

    #Stop keyphrase recognition (just in case it's still running)
    misty.stop_key_phrase_recognition()
    
    # Reset the audio service to avoid needing a robot reboot
    misty.disable_audio_service()
    misty.enable_audio_service()

    start_listening()


# Start program

start_listening()
#restart_listening()
misty.keep_alive()

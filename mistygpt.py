import os
import sys
from mistyPy.Robot import Robot
from mistyPy.Events import Events
import time
import random
import requests
from langchain_community.embeddings import OpenAIEmbeddings



from dotenv import load_dotenv

# Load Misty's IP from environment variables
load_dotenv()
MISTY_IP = os.getenv("MISTY_IP")
if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

# Initialize Misty
misty = Robot(MISTY_IP)
#Robot default
misty.set_default_volume(50)

#To install dependencies use pip install langchain_community,  pip install openai and pip install constants
import constants
from langchain_community.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI

os.environ["OPENAI_API_KEY"] = constants.APIKEY
print("API key loaded")

#query = sys.argv[1]

loader = TextLoader('Data.txt')
print("data.txt is loaded")
#loader = DirectoryLoader(".", glob="*.txt")
# index = VectorstoreIndexCreator().from_loaders([loader]

embedding = OpenAIEmbeddings()
index = VectorstoreIndexCreator(embedding=embedding).from_loaders([loader])


def speech_captured(data):
    #print("speech_captured called with data:", data)  # ADD THIS
    if data["message"]["step"] == "CompletedASR":
        user_input = data["message"]["text"]
        process_user_input(user_input)
        #print("Recognized speech:", user_input)


def process_user_input(user_input):
    mistyOutput = index.query(user_input, llm=ChatOpenAI())
    #print(mistyOutput)
    moveArms = "move my arms"
    moveHead = "move my head"
    moveForward = "go forward"
    moveBackward = "go backward"
    moveForGesture1 = "intelligence"
    lowerVolume = "lower my volume"
    higherVolume = "higher my volume"
    changeDisplay= "change my display"
    
    playDomo = "play domo arrigato"
    playSong = "I’ll play something catchy"
    showVideo = "show me a video"
    displayVideo = "display a video"


    print(mistyOutput)
    #misty.speak_and_listen(mistyOutput)
    misty.speak(mistyOutput)

    if moveForGesture1 in mistyOutput:
        misty.move_arms(-70, 50, 40, 40)
        time.sleep(1)
        print("left arm moved")
        misty.move_arms(50, 50, 40, 40)
    elif moveArms in mistyOutput:
        misty.move_arms(-50, -50, 40, 40)
        time.sleep(2)
        misty.move_arms(50, 50, 40, 40)
        print("arms moved")
    elif moveHead in mistyOutput:
        misty.move_head(0, -25, 0, 100, None, None)
        time.sleep(2)
        misty.move_head(0, 25, 0, 100, None, None)
        time.sleep(2)
        misty.move_head(0, 0, 0, 100, None, None)
        print("arms moved")
    elif moveForward in mistyOutput:
        misty.drive_time(5000,1,5000,0)
        print("moving forward")
    elif moveBackward in mistyOutput:
        misty.drive_time(-5000,1,5000,0)
        print("moving forward")
    elif lowerVolume in mistyOutput:
        misty.set_default_volume(50)
    elif higherVolume in mistyOutput:
        misty.set_default_volume(100)
    elif changeDisplay in mistyOutput:
        misty.display_image("e_JoyGoofy3.jpg")
        time.sleep(3)
        misty.display_image("e_EcstacyHilarious.jpg")
        time.sleep(3)
        misty.display_image("e_defaultcontent.jpg")
    if playDomo in mistyOutput.lower():
        misty.play_audio("domoarrigato.mp3")  # Replace with your actual audio file name
        print("Playing Domo Arigato")

    if playSong in mistyOutput.lower():
        print("Playing a song1")
        misty.play_audio("sound.mp3")  # Replace with any song you've uploaded
        print("Playing a song")

    if showVideo in mistyOutput.lower() or displayVideo in mistyOutput.lower():
        misty.display_video("RickRoll.mp4")  # Replace with your actual video file
        print("Displaying a video")


def recognized(data):
    print(data)  
    misty.speak("Yay, Hi " + data["message"]["label"], 1)
    misty.stop_face_recognition()
    time.sleep(2)
    # misty.start_dialog()
    # misty.speak_and_listen("How can I help you today", utteranceId="required-for-callback")

#If Misty is lifted she gets a bit touchy about that.
def touch_sensor(data):
    if data["message"]["sensorId"] == "cap" and data["message"]["isContacted"] == True:
        touched_sensor = data["message"]["sensorPosition"]
        print(touched_sensor)
        if touched_sensor == "Scruff":
            misty.play_audio("s_Rage.wav")
            misty.display_image("e_Anger.jpg")
            time.sleep(3)
           #Triggers face recognition event to initate ChatGPT
        if touched_sensor == "HeadFront": 
            misty.move_head( -5, 0, 0, 85, None, None)
            misty.display_image("e_Joy2.jpg")
            misty.speak("Aha")
            time.sleep(1)
            misty.start_face_recognition()
            #Stops ChatGPT event
        if touched_sensor == "Chin":
            misty.move_head(0, -50, 0, 150, None, None)
            misty.play_audio("s_Love.wav")
            misty.display_image("e_Love.jpg")
            time.sleep(2)
            misty.display_image("e_DefaultContent.jpg")
            misty.unregister_event("arbitrary-name")

misty.register_event(event_name="touch-sensor",
                     event_type=Events.TouchSensor,
                     callback_function=touch_sensor,
                     keep_alive=True)


misty.register_event(event_name="arbitrary-name",
                     event_type=Events.DialogAction,
                     callback_function=speech_captured,
                     keep_alive=True)

misty.register_event(event_name='face_recognition_event', 
                     event_type=Events.FaceRecognition, 
                     callback_function=recognized, 
                     keep_alive=False)

#misty.speak(index.query(query, llm=ChatOpenAI()))
    

def typed_input_mode():
    print("Entering manual input mode. Type a command and press enter. Type 'exit' to quit.")
    while True:
        user_input = input(">>> ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting manual input mode.")
            break
        if user_input:
            process_user_input(user_input)

import threading

def idle_animation():
    while True:
        misty.display_image("e_DefaultContent.jpg")
        misty.move_arms(30, 30, 40, 40)
        misty.move_head(0, 0, 0, 85, None, None)
        time.sleep(5)
        misty.display_image("e_ContentLeft.jpg")
        time.sleep(3)
        misty.move_arms(20, 10, 40, 40)
        time.sleep(2)
        misty.move_head(0, -10, 0, 60, None, None)
        time.sleep(5)
        misty.display_image("e_ContentRight.jpg")
        time.sleep(3)
        misty.move_head(0, 10, 0, 60, None, None)
        time.sleep(5)
        misty.move_arms(10, 20, 40, 40)

# Start idle animations in the background
threading.Thread(target=idle_animation, daemon=True).start()

# Start manual typed input
typed_input_mode()


misty.keep_alive()
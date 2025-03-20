# Python SDK

Python library to work with the  Misty robot. Currently in BETA. It is designed to follow a Pythonicated version of the naming convention within the [API Explorer](http://sdk.mistyrobotics.com/api-explorer/index.html).
There is a method generator built in to update the built in methods and available events, this works on all current Misty II product versions.

## Requirements

python >= 3.8

requests>=2.25.1<br>
websocket-client<=0.57.0<br>
yapf>=0.30.0
___

# Notes

Past this point is for my personal notes and documentation on the Python-SDK for working with Misty, harvested from Misty Lessons or the [API documentation.](https://docs.mistyrobotics.com/misty-ii/web-api/api-reference/)

On https://lessons.mistyrobotics.com/python/python-lessons/lesson-3-create-memories, Challenge 1, the first argument should be base64, not 65

On https://lessons.mistyrobotics.com/python-elements/misty-python-api/get-assets ```get_video_recording_list()``` should be ```get_video_recording```s_list()``` instead

# Recording a 5 second video
```
misty.start_recording_video(fileName=misty_video_filename, mute=False, duration=5, width=1920, height=1080)
```

I've tried ```width = 3840``` and ```height = 2160``` which works, but swapping it results in the video not saving.

# Retrieve the list of recorded videos on Misty
```
video_list_response = misty.get_video_recording```s_list()

if video_list_response.statu```s_code == 200:
    video_list = video_list_response.json().get("result", [])
    
    if video_list:
        print("Videos stored on Misty:")
        for video in video_list:
            print("-", video)
    else:
        print("No videos found on Misty's storage.")
else:
    print(f"Failed to retrieve video list: {video_list_response.text}")
```
# Retrieve and save the video

```
response = misty.get_video_recording(misty_video_filename, base64=False)

if response.status_code == 200:
    with open(local_video_filename, "wb") as video_file:
        video_file.write(response.content)
    print(f"Video saved as {local_video_filename}")
else:
    print(f"Failed to retrieve video: {response.text}")
```

# Available attributes
```print dir(Events)``` returns:
```
['ActuatorPosition', 'ArTagDetection', 'AudioPlayComplete', 'BatteryCharge', 'BumpSensor', 'ChargerPoseMessage', 'CriticalStatusMessage', 'DialogAction', 'DriveEncoders', 'FaceRecognition', 'FaceTraining', 'HaltCommand', 'HazardNotification', 'IMU', 'KeyPhraseRecognized', 'LocomotionCommand', 'ObjectDetection', 'ObstacleMap', 'PRUMessage', 'PoseEstimation', 'RfCommMessage', 'RfCommState', 'RobotCommandMessage', 'RobotInteractionState', 'SelfState', 'SerialMessage', 'SkillData', 'SkillSystemStateChange', 'SlamStatus', 'SourceFocusConfigMessage', 'SourceTrackDataMessage', 'TextToSpeechComplete', 'TimeOfFlight', 'TouchSensor', 'UserSkillData', 'VoiceRecord', 'WorldState', '__clas```s__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__g```e__', '__getattribut```e__', '__getstat```e__', '__gt__', '__hash__', '__init__', '__init_subclas```s__', '__l```e__', '__lt__', '__modul```e__', '__n```e__', '__new__', '__reduc```e__', '__reduc```e_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'availabl```e_events']
```

# 🎵 Misty Audio Files

<details>
<summary>Custom Sounds</summary>
<br>

```capture_Dialogue.wav```
```newvoice1.mp3```
```voice.wav```
</details>

<details>
<summary>Emotion Sounds</summary>
<br>

```s_Acceptance.wav```
```s_Amazement.wav```
```s_Amazement2.wav```
```s_Awe.wav```
```s_Awe2.wav```
```s_Awe3.wav```
```s_Boredom.wav```
```s_Ecstacy.wav```
```s_Ecstacy2.wav```
```s_Fear.wav```
```s_Joy.wav```
```s_Joy2.wav```
```s_Joy3.wav```
```s_Joy4.wav```
```s_Love.wav```
```s_Grief.wav```
```s_Grief2.wav```
```s_Grief3.wav```
```s_Grief4.wav```
```s_Rage.wav```
```s_Sadness.wav```
```s_Sadness2.wav```
```s_Sadness3.wav```
```s_Sadness4.wav```
```s_Sadness5.wav```
```s_Sadness6.wav```
```s_Sadness7.wav```
```s_Sleepy.wav```
```s_Sleepy2.wav```
```s_Sleepy3.wav```
```s_Sleepy4.wav```
```s_SleepySnore.wav```
```s_Loathing.wav```
```s_Disgust.wav```
```s_Disgust2.wav```
```s_Disgust3.wav```
```s_Disapproval.wav```
</details>

<details>
<summary>Annoyance & Anger Sounds</summary>
<br>

```s_Anger.wav```
```s_Anger2.wav```
```s_Anger3.wav```
```s_Anger4.wav```
```s_Annoyance.wav```
```s_Annoyance2.wav```
```s_Annoyance3.wav```
```s_Annoyance4.wav```
```s_Distraction.wav```
</details>

<details>
<summary>Confusion Sounds</summary>
<br>

```s_DisorientedConfused.wav```
```s_DisorientedConfused2.wav```
```s_DisorientedConfused3.wav```
```s_DisorientedConfused4.wav```
```s_DisorientedConfused5.wav```
```s_DisorientedConfused6.wav```
</details>

<details>
<summary>Phrases & Expressions</summary>
<br>

```s_PhraseByeBye.wav```
```s_PhraseEvilAhHa.wav```
```s_PhraseHello.wav```
```s_PhraseNoNoNo.wav```
```s_PhraseOopsy.wav```
```s_PhraseOwOwOw.wav```
```s_PhraseOwwww.wav```
```s_PhraseUhOh.wav```
</details>

<details>
<summary>System Sounds</summary>
<br>

```s_SystemCameraShutter.wav```
```s_SystemFailure.wav```
```s_SystemSuccess.wav```
```s_SystemWakeWord.wav```
</details>

# Misty Images

<details>
<summary>Expressions & Emotions</summary>
<br>

```e_Admiration.jpg (480x272)```
```e_Aggressiveness.jpg (480x272)```
```e_Amazement.jpg (480x272)```
```e_Anger.jpg (480x272)```
```e_ApprehensionConcerned.jpg (480x272)```
```e_Contempt.jpg (480x272)```
```e_ContentLeft.jpg (480x272)```
```e_ContentRight.jpg (480x272)```
```e_DefaultContent.jpg (480x272)```
```e_Disgust.jpg (480x272)```
```e_Disoriented.jpg (480x272)```
```e_EcstacyHilarious.jpg (480x272)```
```e_EcstacyStarryEyed.jpg (480x272)```
```e_Fear.jpg (480x272)```
```e_Grief.jpg (480x272)```
```e_Joy.jpg (480x272)```
```e_Joy2.jpg (480x272)```
```e_JoyGoofy.jpg (480x272)```
```e_JoyGoofy2.jpg (480x272)```
```e_JoyGoofy3.jpg (480x272)```
```e_Love.jpg (480x272)```
```e_Rage.jpg (480x272)```
```e_Rage2.jpg (480x272)```
```e_Rage3.jpg (480x272)```
```e_Rage4.jpg (480x272)```
```e_RemorseShame.jpg (480x272)```
```e_Sadness.jpg (480x272)```
```e_Surprise.jpg (480x272)```
```e_Terror.jpg (480x272)```
```e_Terror2.jpg (480x272)```
```e_TerrorLeft.jpg (480x272)```
```e_TerrorRight.jpg (480x272)```
</details>

<details>
<summary>Sleeping & Tired Expressions</summary>
<br>

```e_Sleeping.jpg (480x272)```
```e_SleepingZZZ.jpg (480x272)```
```e_Sleepy.jpg (480x272)```
```e_Sleepy2.jpg (480x272)```
```e_Sleepy3.jpg (480x272)```
```e_Sleepy4.jpg (480x272)```
</details>

<details>
<summary>System & Utility Images</summary>
<br>

```e_SystemBlackScreen.jpg (480x272)```
```e_SystemBlinkLarge.jpg (480x272)```
```e_SystemBlinkStandard.jpg (480x272)```
```e_SystemCamera.jpg (480x272)```
```e_SystemFlash.jpg (480x272)```
```e_SystemGearPrompt.jpg (480x272)```
```e_SystemLogoPrompt.jpg (480x272)```
</details>


# Some basic commands for Misty reactions

Default expression

```misty.display_image("e_DefaultContent.jpg")```
Joy

```misty.display_image("e_Joy.jpg")```

Playing audio
```misty.play_audio("s_Joy.wav")```

Moving Head
```misty.move_head(20, -20, 0)  # Look up and to the left```

Changing chest LED
```misty.transition_led(0, 90, 0, 0, 255, 0, "Breathe", 800)```

Moving arms
```misty.move_arms(80, -89)```

# To run demo.py

- create a ```.env``` file
- Add a line ```MISTY_IP=XXX.XX.XX.X```
- Replace ```XXX.XX.XX.X``` with your Misty's IP address.
- You can get the address by downloading the Misty app on your phone/tablet, or using the USB method. https://lessons.mistyrobotics.com/misty-lessons/connect-to-misty 



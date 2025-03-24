from mistyPy.Robot import Robot
from mistyPy.Events import Events
import os
from dotenv import load_dotenv

# Load Misty's IP from environment variables
load_dotenv()

#MISTY_IP = os.getenv("MISTY_IP")
MISTY_IP = os.getenv("MISTY_IP_2")

if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

# Initialize Misty
misty = Robot(MISTY_IP)
misty.change_led(0, 255, 0)
misty.display_image("e_DefaultContent.jpg")
    

def handle_battery(data):
    battery_data = data["message"]

    if battery_data["chargePercent"] is not None:
        percent = battery_data["chargePercent"]
        state = battery_data["state"]
        charging = battery_data["isCharging"]

        print(f"🔋 Battery: {percent}% | State: {state} | Charging: {charging}")
        misty.speak(f"My battery is at {int(percent)} percent.")
    else:
        print("⚠️ Battery percentage is null.")
        misty.speak("I could not read my battery level.")

# Register for real-time battery updates
misty.register_event(
    event_name="battery_update",
    event_type=Events.BatteryCharge,
    callback_function=handle_battery,
    keep_alive=False  # Set to True if you want ongoing updates
)


misty.keep_alive()

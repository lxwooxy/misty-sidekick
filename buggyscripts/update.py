import os
from dotenv import load_dotenv
from mistyPy.GenerateRobot import RobotGenerator

# Load environment variables from .env file
load_dotenv()

MISTY_IP = os.getenv("MISTY_IP")

if not MISTY_IP:
    raise ValueError("MISTY_IP environment variable is not set.")

RobotGenerator(MISTY_IP)

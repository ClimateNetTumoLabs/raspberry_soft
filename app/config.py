import os

from dotenv import load_dotenv

load_dotenv()

LOCAL_DB_HOST = os.getenv('LOCAL_DB_HOST', '')
LOCAL_DB_USERNAME = os.getenv('LOCAL_DB_USERNAME', '')
LOCAL_DB_PASSWORD = os.getenv('LOCAL_DB_PASSWORD', '')
LOCAL_DB_DB_NAME = os.getenv('LOCAL_DB_DB_NAME', '')

MQTT_BROKER_ENDPOINT = os.getenv('MQTT_BROKER_ENDPOINT', '')

MQTT_TOPIC = "raspberry/devices2"

DEVICE_ID = os.getenv('DEVICE_ID', '')

# It is recommended to set the value > than
# MAX_READING_TIME + 10
MEASURING_TIME = 900

# It is recommended to set the value >= than
# sum of sensors reading_times
MAX_READING_TIME = 300

SENSORS = {
    "light_sensor": {
        "working": True,
        "reading_time": 60
    },
    "tph_sensor": {
        "working": True,
        "reading_time": 60
    },
    "air_quality_sensor": {
        "working": True,
        "address": "/dev/ttyS0",
        "baudrate": 9600,
        "pin_enable": 22,
        "pin_enable_working": False,
        "pin_reset": 27,
        "pin_reset_working": False,
        "reading_time": 60
    },
    "wind_speed": {
        "working": True,
        "pin": 5
    },
    "wind_direction": {
        "working": True,
        "reading_time": 10
    },
    "rain": {
        "working": True,
        "pin": 6
    }
}

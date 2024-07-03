import os

from dotenv import load_dotenv

load_dotenv()

LOCAL_DB_DB_NAME = os.getenv('LOCAL_DB_DB_NAME', '')

MQTT_BROKER_ENDPOINT = os.getenv('MQTT_BROKER_ENDPOINT', '')

MQTT_TOPIC = "raspberry/devices"

DEVICE_ID = os.getenv('DEVICE_ID', '')

# It is recommended to set the value > than
# MAX_READING_TIME + 10
MEASURING_TIME = 900

# It is recommended to set the value >= than
# sum of sensors reading_times
MAX_READING_TIME = 300

SENSORS = {
    "light_sensor": {
        "working": True
    },
    "tph_sensor": {
        "working": True,
        "port": 1
    },
    "air_quality_sensor": {
        "working": True,
        "address": "/dev/ttyAMA0",
        "baudrate": 9600,
        "pin_enable": 22,
        "pin_enable_working": False,
        "pin_reset": 27,
        "pin_reset_working": False
    },
    "wind_speed": {
        "working": True,
        "pin": 5
    },
    "wind_direction": {
        "working": True,
        "reading_time": 10,
        "adc_channel": 0,
        "config_file": "directions_config.json",
        "adc_max": 1024,
        "adc_vref": 5.12
    },
    "rain": {
        "working": True,
        "pin": 6,
        "bucket_size": 0.2794
    }
}

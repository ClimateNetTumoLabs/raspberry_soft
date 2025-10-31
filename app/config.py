import os

from dotenv import load_dotenv

load_dotenv()

LOCAL_DB = os.getenv('LOCAL_DB', '')
MQTT_BROKER_ENDPOINT = os.getenv('MQTT_BROKER_ENDPOINT', '')
MQTT_TOPIC = os.getenv('MQTT_TOPIC', '')
DEVICE_ID = os.getenv('DEVICE_ID', '')

# It is recommended to set the value > than
# MEASURING_TIME + 10
TRANSMISSION_INTERVAL = 900

# It is recommended to set the value >= than
# sum of sensors reading_times
MEASURING_TIME = 300
READING_TIME = 30

SENSORS = {
    "light_sensor": {
        "working": True,
        "scl": "SCL",
        "sda": "SDA",
        "address": 0x53
    },
    "tph_sensor": {
        "working": True,
        "port": 1,
        "address": 0x76
    },
    "air_pollution_PMS5003": {
        "working": True,
        "address": "/dev/ttyAMA0",
        "baudrate": 9600,
        "pin_enable": 22,
        "pin_enable_working": False,
        "pin_reset": 27,
        "pin_reset_working": False
    },
    "air_pollution_sps30": {
        "working": True,
        "port": 1,
        "warmup": 30,
        "autoclean": True
    },
    "wind_speed": {
        "working": True,
        "pin": 5,
        "speed_coefficient": 2.4,
        "interval_sec": 30,
    },
    "wind_direction": {
        "working": True,
        "adc_channel": 0,
        "adc_max": 1024,
        "adc_vref": 5.12,
        "tolerance": 0.1
    },
    "rain": {
        "working": True,
        "pin": 6,
        "bucket_size": 0.2794
    }
}
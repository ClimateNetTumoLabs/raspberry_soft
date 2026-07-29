import os

from dotenv import load_dotenv

load_dotenv()

LOCAL_DB = os.getenv('LOCAL_DB', '')
MQTT_BROKER_ENDPOINT = os.getenv('MQTT_BROKER_ENDPOINT', '')
MQTT_TOPIC = os.getenv('MQTT_TOPIC', '')
# Topic the Lambda publishes delivery confirmations to. Must resolve to the same
# string as ACK_TOPIC_TEMPLATE in the Lambda's config; a mismatch is silent -
# acks never arrive and records buffer forever.
MQTT_ACK_TOPIC = os.getenv('MQTT_ACK_TOPIC', '')
DEVICE_ID = os.getenv('DEVICE_ID', '')

SSID = ""
PASSWORD = ""
# It is recommended to set the value > than
# MEASURING_TIME + 10
TRANSMISSION_INTERVAL = 900

# It is recommended to set the value >= than
# sum of sensors reading_times
MEASURING_TIME = 300
READING_TIME = 30

# Seconds to wait for the Lambda to confirm a batch reached the database.
# Covers a cold start against a VPC-attached RDS.
ACK_TIMEOUT = 20

# Records per publish. AWS IoT Core rejects payloads larger than 128 KB.
SEND_CHUNK_SIZE = 100

SENSORS = {
    "ltr390": {
        "working": True,
        "address": 0x53
    },
    "bme280": {
        "working": True,
        "port": 1,
        "address": 0x76
    },
    "pms5003": {
        "working": False,
        "address": "/dev/ttyAMA0",
        "baudrate": 9600,
        "pin_enable": 22,
        "pin_enable_working": False,
        "pin_reset": 27,
        "pin_reset_working": False
    },
    "sps30": {
        "warmup": 30,
        "uart": {
            "working": True,
            "address": "/dev/ttyAMA0",
            "baudrate": 115200,
            "timeout": 1
        },
        "i2c": {
            "working": False,
            "port": 1,
        },
    },
    "speed": {
        "working": True,
        "pin": 5,
        "speed_coefficient": 2.4,
        "interval_sec": 30,
    },
    "direction": {
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
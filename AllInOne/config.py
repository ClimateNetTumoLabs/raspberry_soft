DEVICE_ID = None

# It is recommended to set the value >= than
# MAX_READING_TIME + wind_direction["reading_time"] + 10
MEASURING_TIME = 900
MAX_READING_TIME = 100

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

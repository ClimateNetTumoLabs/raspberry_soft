DEVICE_ID = 9

# It is recommended to set the value >= than 
# MAX_READING_TIME + wind_direction["reading_time"] + 10
MEASURING_TIME = 60
MAX_READING_TIME = 40


SENSORS = {
    "light_sensor" : {
        "working": True
    },
    "tph_sensor" : {
        "working": True
    },
    "air_quality_sensor": {
        "working": True,
        "address": "/dev/ttyS0",
        "baudrate": 9600,
        "pin_enable": 27,
        "pin_reset": 22
    },
    "wind_speed": {
        "working": True,
        "pin": 5
    },
    "wind_direction": {
        "woking": True,
        "reading_time": 10
    },
    "rain": {
        "working": True,
        "pin": 6
    },
    "altitude": {
        "working": True
    }
}

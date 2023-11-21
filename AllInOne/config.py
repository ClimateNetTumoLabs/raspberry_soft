DEVICE_ID = 9

MEASURING_TIME = 60
MAX_READING_TIME = 40
WIND_DIRECTION_READING_TIME = 10


SENSORS = {
    "light_sensor" : True,
    "tph_sensor" : True,
    "air_quality_sensor": True,
    "wind_speed": True,
    "wind_direction": True,
    "rain": True
}


# AIR QUALITY SENSOR SETTINGS
PMS5003_ADDRESS = "/dev/ttyS0"
PMS5003_BAUDRATE = 9600
PMS5003_PIN_ENABLE = 27
PMS5003_PIN_RESET = 22


# WEATHER METER KIT
RAIN_PIN = 6
SPEED_PIN = 5
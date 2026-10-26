"""
Metrological settings: values that change what a station reports.

They are covered by version.metro_checksum(), so they must stay plain
constants. Never read them from .env, a file or the network - a change to
any of them must only ever arrive as a new software version.
"""

# Seconds of measuring before each transmission. It is recommended to set
# the value >= the sum of the sensors' reading times.
MEASURING_TIME = 300

# Seconds between single readings inside the measuring period.
READING_TIME = 30

# Seconds the SPS30 runs before its readings count.
SPS30_WARMUP = 30

# SPS30 operating limits. Outside them the SPS30 is not started and PM is sent
# as null. Inclusive: exactly -10 °C, 60 °C or 95 % is within the limits.
SPS30_MIN_TEMPERATURE = -10   # °C
SPS30_MAX_TEMPERATURE = 60    # °C
SPS30_MAX_HUMIDITY = 95       # %RH

# Anemometer: km/h per pulse per second.
WIND_SPEED_COEFFICIENT = 2.4

# Wind vane: calibrated output voltage for each of the 16 directions (degrees: volts).
WIND_DIRECTION_VOLTAGES = {
    0.0: 3.84, 22.5: 1.98, 45.0: 2.25, 67.5: 0.41,
    90.0: 0.45, 112.5: 0.32, 135.0: 0.90, 157.5: 0.62,
    180.0: 1.40, 202.5: 1.19, 225.0: 3.08, 247.5: 2.93,
    270.0: 4.62, 292.5: 4.04, 315.0: 4.33, 337.5: 3.43
}


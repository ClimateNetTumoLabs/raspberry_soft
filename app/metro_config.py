"""
Metrological settings: values that change what a station reports.

They are covered by version.metro_checksum(), so they must stay plain
constants. Never read them from .env, a file or the network - a change to
any of them must only ever arrive as a new software version.
"""

# Seconds of measuring before each transmission: the standard 10-min mean
# (WMO-No. 8, Annex 1.A and §5.8.1).
MEASURING_TIME = 600

# Seconds between temperature, humidity, pressure, light and PM readings. Faster
# than the sensor time constants (about 20 s for temperature, 40 s for RH, Annex 1.A).
READING_TIME = 10

# Seconds between paired wind speed and direction readings (non-overlapping 3-s
# samples, WMO-No. 8 §5.8.3). Direction is their speed-weighted vector mean.
WIND_READING_TIME = 3

# Mean wind speed at or below this is calm, sent with no direction (WMO-No. 8 §5.1).
WIND_CALM = 0.2  # m/s

# Seconds the SPS30 runs before its readings count. Runs before the measuring
# window starts, so it doesn't shorten it.
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

# SPS30 PM10 correction (sensors/pm10_model.py): spread (geometric standard deviation)
# of the particle size distribution. 2.0 is a textbook value for mixed indoor/urban air;
# bigger = higher PM10 for the same PM2.5. Re-fit it against a reference PM10 instrument.
SPS30_PM10_GSD = 2.0

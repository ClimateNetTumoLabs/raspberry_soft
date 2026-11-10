"""
SPS30 PM10 correction from the typical particle size (TPS).

The SPS30 barely sees particles above 2.5 um. Its PM4/PM10 and its number counts
NC4/NC10 are extrapolated from the smaller sizes (datasheet), so its PM10 sits almost
on top of PM2.5. Here the size distribution is taken as lognormal with geometric
standard deviation `gsd`. TPS is the number-mean diameter, which gives the mass median
diameter MMD = TPS * exp(2.5 ln^2 gsd) (Hatch-Choate). PM10 is then
PM2.5 * (mass fraction below 10 um) / (mass fraction below 2.5 um).

Same formula as pm10FromTps() in the ESP32 firmware (esp_soft/pm10_model.h).
"""
import math


def pm10_from_tps(pm25, pm10_raw, tps, gsd):
    if pm25 is None or tps is None or not tps > 0:
        return pm10_raw                                  # no TPS: keep the sensor's own value
    s = math.log(gsd)
    mmd = tps * math.exp(2.5 * s * s)
    below = lambda d: 0.5 * math.erfc(-math.log(d / mmd) / (s * math.sqrt(2)))
    # ponytail: cap 3 stops a glitchy TPS from blowing PM10 up; raise it if you log real dust storms.
    ratio = min(below(10) / below(2.5), 3.0)
    return max(pm10_raw or 0.0, pm25 * ratio)            # never below what the sensor itself reports

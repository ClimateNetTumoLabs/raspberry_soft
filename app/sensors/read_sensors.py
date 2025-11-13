from bme280 import BME280Sensor
from ltr390 import LTR390Sensor
from sps30 import SPS30Sensor
from rain import RainSensor
from wind import WindSpeedSensor, WindDirectionSensor

sensors = {
    "tph": BME280Sensor,
    "light": LTR390Sensor,
    "airQuality": SPS30Sensor,
    "speed": WindSpeedSensor,
    "rain": RainSensor,
    "direction": WindDirectionSensor
}
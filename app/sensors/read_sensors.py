from .tph import TPHSensor
from .ltr390 import LTR390Sensor
from .air_quality import AirQualitySensor
from .rain import RainSensor
from .wind import WindSpeedSensor, WindDirectionSensor

sensors = {
    "tph": TPHSensor,
    "light": LTR390Sensor,
    "airQuality": AirQualitySensor,
    "speed": WindSpeedSensor,
    "rain": RainSensor,
    "direction": WindDirectionSensor
}
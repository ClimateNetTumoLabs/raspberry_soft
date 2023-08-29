import time
from Sensors.WindDirectionSensor import WindDirection
from Sensors.WindSpeedSensor import WindSpeed
from Sensors.RainSensor import Rain


class Sensors:
    """
    A class representing a collection of sensors for wind direction, wind speed, and rain measurements.

    Attributes:
        direction (WindDirection): The WindDirection sensor instance.
        speed (WindSpeed): The WindSpeed sensor instance.
        rain (Rain): The Rain sensor instance.
        parse_interval (int): The time interval (in seconds) for collecting data from sensors.

    Methods:
        reset_all(): Resets all sensor data.
        get_data(): Collects and returns data from all sensors over the specified interval.
    """

    def __init__(self, parse_interval=20):
        """
        Initializes the Sensors class with instances of WindDirection, WindSpeed, and Rain sensors.
        Also sets up callbacks for sensor press events.

        Args:
            parse_interval (int, optional): The time interval (in seconds) for collecting sensor data.
                                            Defaults to 20 seconds.
        """
        self.direction = WindDirection()
        self.speed = WindSpeed()
        self.rain = Rain()

        self.parse_interval = parse_interval

        self.speed.sensor.when_pressed = self.speed.press
        self.rain.sensor.when_pressed = self.rain.press

    def reset_all(self):
        """
        Resets data for all sensors.
        """
        self.speed.reset()
        self.rain.reset()
        self.direction.reset()

    def get_data(self):
        """
        Collects data from sensors over the specified interval and returns the results.

        Returns:
            dict: A dictionary containing rain, wind speed, and wind direction data.
        """
        start_time = time.time()
        old_speed_count = 0

        while time.time() - start_time <= self.parse_interval:
            if self.speed.count != old_speed_count:
                old_speed_count = self.speed.count
                self.direction.add_data()

        result = {
            "speed": self.speed.get_data(self.parse_interval),
            "rain": self.rain.get_data(),
            "direction": self.direction.get_data()
        }

        self.reset_all()

        return result


def main():
    sensors = Sensors()

    while True:
        res = sensors.get_data()

        print(f"Rain: {res['rain']} mm")
        print(f"Speed: {res['speed']} km/h")
        print(f"Direction: {res['direction']}")
        
        print("\n" + "#" * 50 + "\n")


if __name__=="__main__":
    main()

from gpiozero import Button
import time


class WindSpeedSensor():
    """
    A class representing a wind speed sensor based on a rotational mechanism.

    Attributes:
        gpio_pin (int): The GPIO pin number connected to the wind speed sensor.
        wind_interval (int): The time interval (in seconds) for calculating wind speed.
        turn_distance (float): The distance (in arbitrary units) traveled per wind event.
        wind_speed_sensor (gpiozero.Button): Button object representing the wind speed sensor.
        wind_count (int): Counter for the number of wind events.

    Methods:
        spin(): Callback function triggered when the wind speed sensor is pressed (wind event detected).
        calculate_speed(): Calculates the wind speed based on the number of wind events and wind interval.
        get_data(): Gets wind speed data after waiting for the specified wind interval.
    """

    def __init__(self, gpio_pin=5, wind_interval=5, turn_distance=2.4):
        """
        Initializes the WindSpeedSensor with the specified GPIO pin, wind interval, and turn distance.

        Args:
            gpio_pin (int, optional): The GPIO pin number connected to the wind speed sensor.
                                     Defaults to 5.
            wind_interval (int, optional): The time interval (in seconds) for calculating wind speed.
                                           Defaults to 5 seconds.
            turn_distance (float, optional): The distance (in arbitrary units) traveled per wind event.
                                             Defaults to 2.4 units.
        """
        self.gpio_pin = gpio_pin
        self.wind_interval = wind_interval
        self.wind_speed_sensor = Button(gpio_pin)
        self.wind_count = 0
        self.wind_speed_sensor.when_pressed = self.spin
        self.turn_distance = turn_distance

    def spin(self):
        """
        Callback function triggered when the wind speed sensor is pressed (wind event detected).
        It increments the wind count by 1.
        """
        self.wind_count += 1

    def calculate_speed(self):
        """
        Calculates the wind speed based on the number of wind events, wind interval, and turn distance.

        Returns:
            float: The calculated wind speed in arbitrary units per hour.
        """
        speed_km_h = ((self.wind_count / self.wind_interval) * self.turn_distance)
        return speed_km_h

    def get_data(self):
        """
        Gets wind speed data after waiting for the specified wind interval.

        Returns:
            float: The wind speed data in arbitrary units per hour.
        """
        time.sleep(self.wind_interval)
        data = self.calculate_speed()
        self.wind_count = 0
        return data


if __name__ == "__main__":
    wind_speed_sensor = WindSpeedSensor()
    while True:
        res = wind_speed_sensor.get_data()
        print(f"{round(res, 2)} km/h")
        print("\n" + ("#" * 10) + "\n")


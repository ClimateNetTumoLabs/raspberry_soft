from PMS5003_library import PMS5003


class AirQualitySensor:
    """
    A class representing an air quality sensor using the PMS5003 particulate matter sensor.

    Attributes:
        device (str): The serial port device file for communication with the sensor. Default is '/dev/ttyS0'.
        baudrate (int): The baud rate for serial communication. Default is 9600.
        pin_enable (int): The GPIO pin number connected to the sensor's enable pin. Default is 27.
        pin_reset (int): The GPIO pin number connected to the sensor's reset pin. Default is 22.

    Methods:
        read_data(): Reads air quality data from the PMS5003 sensor and returns a dictionary of measurements.
    """

    def __init__(self, device='/dev/ttyS0', baudrate=9600, pin_enable=27, pin_reset=22):
        """
        Initializes the AirQualitySensor with the specified device, baud rate, and GPIO pins.

        Args:
            device (str, optional): The serial port device file for communication with the sensor.
                                    Defaults to '/dev/ttyS0'.
            baudrate (int, optional): The baud rate for serial communication. Defaults to 9600.
            pin_enable (int, optional): The GPIO pin number connected to the sensor's enable pin. Defaults to 27.
            pin_reset (int, optional): The GPIO pin number connected to the sensor's reset pin. Defaults to 22.
        """
        self.device = device
        self.baudrate = baudrate
        self.pin_enable = pin_enable
        self.pin_reset = pin_reset
        self.pms5003 = PMS5003(device=device, baudrate=baudrate, pin_enable=pin_enable, pin_reset=pin_reset)

    def read_data(self):
        """
        Reads air quality data from the PMS5003 sensor and returns a dictionary of measurements.

        Returns:
            dict: A dictionary containing various air quality measurements such as PM1, PM2.5, PM10, etc.
        """
        data = {}
        all_data = self.pms5003.read()

        data["PM1"] = all_data.pm_ug_per_m3(1.0)
        data["PM2_5"] = all_data.pm_ug_per_m3(2.5)
        data["PM10"] = all_data.pm_ug_per_m3(10)
        data["Atmospheric_PM1"] = all_data.pm_ug_per_m3(1.0, True)
        data["Atmospheric_PM2_5"] = all_data.pm_ug_per_m3(2.5, True)
        data["Atmospheric_PM10"] = all_data.pm_ug_per_m3(10, True)

        data["0_3um"] = all_data.pm_per_1l_air(0.3)
        data["0_5um"] = all_data.pm_per_1l_air(0.5)
        data["1_0um"] = all_data.pm_per_1l_air(1.0)
        data["2_5um"] = all_data.pm_per_1l_air(2.5)
        data["5um"] = all_data.pm_per_1l_air(5)
        data["10um"] = all_data.pm_per_1l_air(10)

        return data

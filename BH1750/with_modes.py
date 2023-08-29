import smbus2
import time


class BH1750():
    # Constants for different modes and settings of the sensor
    POWER_DOWN = 0x00    # No active state
    POWER_ON = 0x01      # Power on
    RESET = 0x07         # Reset data register value

    CONTINUOUS_LOW_RES_MODE = 0x13    # Start measurement at 4lx resolution. Time typically 16ms.
    CONTINUOUS_HIGH_RES_MODE_1 = 0x10 # Start measurement at 1lx resolution. Time typically 120ms
    CONTINUOUS_HIGH_RES_MODE_2 = 0x11 # Start measurement at 0.5lx resolution. Time typically 120ms

    ONE_TIME_LOW_RES_MODE = 0x23      # Start measurement at 1lx resolution. Time typically 120ms
    ONE_TIME_HIGH_RES_MODE_1 = 0x20   # Start measurement at 1lx resolution. Time typically 120ms
    ONE_TIME_HIGH_RES_MODE_2 = 0x21   # Start measurement at 0.5lx resolution. Time typically 120ms

    def __init__(self, bus, addr=0x23):
        """ 
        Initialize the BH1750 sensor object with I2C bus and address.
        The sensor is set to a default state with power down and sensitivity setting.
        """
        self.bus = bus
        self.addr = addr
        self.power_down()
        self.set_sensitivity()

    def _set_mode(self, mode):
        """
        Internal method to set the measurement mode of the sensor.
        """
        self.mode = mode
        self.bus.write_byte(self.addr, self.mode)

    def power_down(self):
        """
        Put the sensor in power-down mode (no active state).
        """
        self._set_mode(self.POWER_DOWN)

    def power_on(self):
        """
        Power on the sensor.
        """
        self._set_mode(self.POWER_ON)

    def reset(self):
        """
        Reset the sensor's data register value.
        Note: It has to be powered on before resetting.
        """
        self.power_on()
        self._set_mode(self.RESET)

    def cont_low_res(self):
        """ Set the sensor to continuous low-resolution measurement mode. """
        self._set_mode(self.CONTINUOUS_LOW_RES_MODE)

    def cont_high_res(self):
        """ Set the sensor to continuous high-resolution measurement mode 1. """
        self._set_mode(self.CONTINUOUS_HIGH_RES_MODE_1)

    def cont_high_res2(self):
        """ Set the sensor to continuous high-resolution measurement mode 2. """
        self._set_mode(self.CONTINUOUS_HIGH_RES_MODE_2)

    def oneshot_low_res(self):
        """ Perform a one-time low-resolution measurement. """
        self._set_mode(self.ONE_TIME_LOW_RES_MODE)

    def oneshot_high_res(self):
        """ Perform a one-time high-resolution measurement mode 1. """
        self._set_mode(self.ONE_TIME_HIGH_RES_MODE_1)

    def oneshot_high_res2(self):
        """ Perform a one-time high-resolution measurement mode 2. """
        self._set_mode(self.ONE_TIME_HIGH_RES_MODE_2)

    def set_sensitivity(self, sensitivity=69):
        """
        Set the sensor sensitivity.
        Valid values are 31 (lowest) to 254 (highest), default is 69.
        """
        if sensitivity < 31:
            self.mtreg = 31
        elif sensitivity > 254:
            self.mtreg = 254
        else:
            self.mtreg = sensitivity
        self.power_on()
        self._set_mode(0x40 | (self.mtreg >> 5))
        self._set_mode(0x60 | (self.mtreg & 0x1f))
        self.power_down()

    def get_result(self):
        """ Return the current measurement result in lux (lx). """
        data = self.bus.read_word_data(self.addr, self.mode)
        count = data >> 8 | (data & 0xff) << 8
        mode2coeff = 2 if (self.mode & 0x03) == 0x01 else 1
        ratio = 1 / (1.2 * (self.mtreg / 69.0) * mode2coeff)
        return ratio * count

    def wait_for_result(self, additional=0):
        """
        Wait for the sensor to complete the measurement.
        The additional parameter adds extra delay to the wait time.
        """
        basetime = 0.018 if (self.mode & 0x03) == 0x03 else 0.128
        time.sleep(basetime * (self.mtreg / 69.0) + additional)

    def do_measurement(self, mode, additional_delay=0):
        """
        Perform a measurement in a specific mode and return the result.
        The additional_delay parameter adds extra delay to the measurement process.
        """
        self.reset()
        self._set_mode(mode)
        self.wait_for_result(additional=additional_delay)
        return self.get_result()

    def measure_low_res(self, additional_delay=0):
        """ Perform a one-time low-resolution measurement and return the result. """
        return self.do_measurement(self.ONE_TIME_LOW_RES_MODE, additional_delay)

    def measure_high_res(self, additional_delay=0):
        """ Perform a one-time high-resolution measurement mode 1 and return the result. """
        return self.do_measurement(self.ONE_TIME_HIGH_RES_MODE_1, additional_delay)

    def measure_high_res2(self, additional_delay=0):
        """ Perform a one-time high-resolution measurement mode 2 and return the result. """
        return self.do_measurement(self.ONE_TIME_HIGH_RES_MODE_2, additional_delay)


def main():
    """ The main function to demonstrate using the BH1750 class for continuous measurement. """
    bus = smbus2.SMBus(1)

    sensor = BH1750(bus)
    sensor.set_sensitivity(254)
    
    try:
        while True:
            print(f"Light Level: {round(sensor.measure_high_res2(), 2)} lx")
            print("--------")

            time.sleep(1)
    except KeyboardInterrupt:
        # Handle the Ctrl+C keyboard interrupt gracefully
        print("Goodbye!")


if __name__ == "__main__":
    main()


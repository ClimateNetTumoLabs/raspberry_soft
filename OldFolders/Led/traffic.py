import RPi.GPIO as GPIO
import time


class TrafficLight():
    """
    A class representing a simulated traffic light using GPIO pins on a Raspberry Pi.

    Attributes:
        GPIO_MODE (int): The GPIO mode used for pin numbering. Default is GPIO.BCM.
        RED (int): The GPIO pin number for the red LED of the traffic light.
        YELLOW (int): The GPIO pin number for the yellow LED of the traffic light.
        GREEN (int): The GPIO pin number for the green LED of the traffic light.

    Methods:
        switch(red, yellow, green, t): Controls the state of the traffic light LEDs for a specified time.
        run(): Simulates a traffic light sequence by cycling through different light states.
    """

    def __init__(self, GPIO_MODE=GPIO.BCM, RED=22, YELLOW=27, GREEN=17):
        """
        Initializes the TrafficLight with the specified GPIO mode and pin numbers.

        Args:
            GPIO_MODE (int, optional): The GPIO mode used for pin numbering. Defaults to GPIO.BCM.
            RED (int, optional): The GPIO pin number for the red LED of the traffic light. Defaults to 22.
            YELLOW (int, optional): The GPIO pin number for the yellow LED of the traffic light. Defaults to 27.
            GREEN (int, optional): The GPIO pin number for the green LED of the traffic light. Defaults to 17.
        """
        GPIO.setmode(GPIO_MODE)

        self.RED = RED
        self.YELLOW = YELLOW
        self.GREEN = GREEN
        
        GPIO.setup(self.RED, GPIO.OUT)
        GPIO.setup(self.YELLOW, GPIO.OUT)
        GPIO.setup(self.GREEN, GPIO.OUT)
    
    def switch(self, red, yellow, green, t):
        """
        Controls the state of the traffic light LEDs for a specified time.

        Args:
            red (int): 1 to turn on the red LED, 0 to turn it off.
            yellow (int): 1 to turn on the yellow LED, 0 to turn it off.
            green (int): 1 to turn on the green LED, 0 to turn it off.
            t (float): The time (in seconds) to maintain the specified LED states.
        """
        GPIO.output(self.RED, red)
        GPIO.output(self.YELLOW, yellow)
        GPIO.output(self.GREEN, green)
        time.sleep(t)

    def run(self):
        """
        Simulates a traffic light sequence by cycling through different light states.

        Press Ctrl+C to exit the sequence and clean up GPIO pins.
        """
        try:
            while True:
                # Red light
                self.switch(1, 0, 0, 3)

                # Yellow light
                self.switch(0, 1, 0, 1)

                # Green light
                self.switch(0, 0, 1, 3)

                # Yellow light
                self.switch(0, 1, 0, 1)
        except KeyboardInterrupt:
            print("Goodbye!")
            GPIO.cleanup()


if __name__=="__main__":
    traffic = TrafficLight()
    traffic.run()

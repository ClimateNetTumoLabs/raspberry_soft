import RPi.GPIO as GPIO
import time

class ChristmasTree:
    """A class representing a Christmas tree with LED lights and a button control.

    Args:
        GPIO_MODE (int): GPIO mode (default: GPIO.BCM).
        RED (int): GPIO pin for the red LED (default: 22).
        YELLOW (int): GPIO pin for the yellow LED (default: 27).
        GREEN (int): GPIO pin for the green LED (default: 17).
        BUTTON (int): GPIO pin for the button (default: 23).

    Attributes:
        RED (int): GPIO pin for the red LED.
        YELLOW (int): GPIO pin for the yellow LED.
        GREEN (int): GPIO pin for the green LED.
        BUTTON (int): GPIO pin for the button.

    Methods:
        all_off(): Turn off all LED lights.
        sleep(t): Pause execution for 't' seconds, with button interrupt support.
        mode1(): Activate mode 1 - cycling through red, yellow, and green LEDs.
        mode2(): Activate mode 2 - blinking LEDs in sequence.
        mode3(): Activate mode 3 - cycling through combinations of red, yellow, and green LEDs.
        run(): Run all modes in a loop until interrupted by KeyboardInterrupt.

    Note:
        This class assumes that the Raspberry Pi GPIO pins are properly set up before usage.
    """

    def __init__(self, GPIO_MODE=GPIO.BCM, RED=22, YELLOW=27, GREEN=17, BUTTON=23):
        """Initialize the ChristmasTree object and set up GPIO pins."""
        GPIO.setmode(GPIO_MODE)

        self.RED = RED
        self.YELLOW = YELLOW
        self.GREEN = GREEN
        self.BUTTON = BUTTON

        GPIO.setup(self.RED, GPIO.OUT)
        GPIO.setup(self.YELLOW, GPIO.OUT)
        GPIO.setup(self.GREEN, GPIO.OUT)

        GPIO.setup(self.BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def all_off(self):
        """Turn off all LED lights."""
        GPIO.output(self.RED, 0)
        GPIO.output(self.YELLOW, 0)
        GPIO.output(self.GREEN, 0)

    def sleep(self, t):
        """Pause execution for a specified time, with button interrupt support.

        Args:
            t (float): Time in seconds to pause execution.

        Returns:
            bool: True if sleep completes, False if interrupted by the button.
        """
        start_time = time.time()
        while time.time() - start_time <= t:
            if GPIO.input(self.BUTTON) == GPIO.LOW:
                time.sleep(0.3)
                self.all_off()
                return False
        return True
    
    def mode1(self):
        """Activate mode 1 - cycling through red, yellow, and green LEDs.

        Returns:
            bool: True if mode completes, False if interrupted by the button.
        """
        while True:
            GPIO.output(self.RED, 1)
            GPIO.output(self.YELLOW, 0)
            GPIO.output(self.GREEN, 0)

            if not self.sleep(1):
                return False

            GPIO.output(self.RED, 0)
            GPIO.output(self.YELLOW, 1)
            GPIO.output(self.GREEN, 0)

            if not self.sleep(1):
                return False

            GPIO.output(self.RED, 0)
            GPIO.output(self.YELLOW, 0)
            GPIO.output(self.GREEN, 1)
            
            if not self.sleep(1):
                return False
    
    def mode2(self):
        """Activate mode 2 - blinking LEDs in sequence.

        Returns:
            bool: True if mode completes, False if interrupted by the button.
        """
        leds = [self.RED, self.YELLOW, self.GREEN]

        while True:
            for led in leds:
                for i in range(5):
                    GPIO.output(led, 1)

                    if not self.sleep(0.1):
                        return False
                    
                    GPIO.output(led, 0)

                    if not self.sleep(0.1):
                        return False
    
    def mode3(self):
        """Activate mode 3 - cycling through combinations of red, yellow, and green LEDs.

        Returns:
            bool: True if mode completes, False if interrupted by the button.
        """
        modes = [[1, 1, 0], [0, 1, 1], [1, 0, 1], [0, 1, 0]]

        while True:
            for mode in modes:
                for i in range(2):
                    GPIO.output(self.RED, mode[0])
                    GPIO.output(self.YELLOW, mode[1])
                    GPIO.output(self.GREEN, mode[2])
                    if not self.sleep(0.7):
                        return False

    def run(self):
        """Run all modes in a loop until interrupted by KeyboardInterrupt.

        This method continuously cycles through all three modes until a KeyboardInterrupt is raised.
        Upon interruption, it prints a goodbye message and cleans up the GPIO pins.
        """
        try:
            while True:
                self.mode1()
                self.mode2()
                self.mode3()
        except KeyboardInterrupt:
            print("Goodbye!")
            GPIO.cleanup()


if __name__=="__main__":
    tree = ChristmasTree()
    tree.run()

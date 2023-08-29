import RPi.GPIO as GPIO
import time


class UltrasonicSensor:
    """
    JSN-SR04T-2.0 Distance Sensor Class
    """

    def __init__(self, TRIG=24, ECHO=23):
        """
        Initialize the JSN-SR04T Ultrasonic Distance Sensor.

        Args:
            TRIG (int): GPIO pin number for the trigger signal (default is 24).
            ECHO (int): GPIO pin number for the echo signal (default is 23).
        """
        self.TRIG = TRIG
        self.ECHO = ECHO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)

    def read_data(self):
        """
        Read the distance from the JSN-SR04T sensor.

        Returns:
            float: The distance in centimeters. Returns 0 if the distance is out of range (less than 20 or greater than 400).
        """
        GPIO.output(self.TRIG, False)
        time.sleep(2)

        GPIO.output(self.TRIG, True)
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        pulse_start = time.time()
        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()

        pulse_end = time.time()
        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17150
        distance = round(distance, 2)

        if 20 < distance < 400:
            return distance
        else:
            return 0


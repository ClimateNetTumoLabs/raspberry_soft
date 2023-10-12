import RPi.GPIO as GPIO
import time
from threading import Thread

# Set the GPIO mode to BOARD (using physical pin numbering)
GPIO.setmode(GPIO.BOARD)

# Define the GPIO pins for TRIG, ECHO, and BUZZER
TRIG = 15
ECHO = 13
BUZZER = 16

# Inform the user that distance measurement is in progress
print("Distance measurement in progress")

# Setup the GPIO pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

# Create a PWM object for the buzzer and start with 0 duty cycle
buzz = GPIO.PWM(BUZZER, 1)
buzz.start(0)


class Distance:
    l = 600
    t = 0.25
    last_distances = [0, 0]
    low = False


# Function to change the parameters of the buzzer (frequency and time) and update low state
def change_params(frequency, time, low, obj):
    buzz.ChangeFrequency(frequency)
    obj.t = time
    obj.low = low


# Function to measure the distance using ultrasonic sensor
def get_distance():
    # Send a short pulse to the TRIG pin
    GPIO.output(TRIG, False)
    time.sleep(2)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Measure the time taken for the pulse to return (echo duration)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    # Calculate the distance in centimeters using the speed of sound (17150 cm/s)
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance


# Function to control the buzzer based on distance thresholds
def low_distance(obj):
    while True:
        if obj.l < 30:
            change_params(500, 0.2, True, obj)
        elif obj.l < 40:
            change_params(400, 0.5, True, obj)
        elif obj.l < 50:
            change_params(300, 1, True, obj)
        elif obj.last_distances[0] < 30 and obj.last_distances[1] < 30:
            change_params(600, 0.1, False, obj)
        else:
            time.sleep(2)
            continue

        if obj.low:
            del obj.last_distances[0]
            obj.last_distances.append(obj.l)

        buzz.ChangeDutyCycle(50)
        time.sleep(obj.t)
        buzz.ChangeDutyCycle(0)
        time.sleep(obj.t)


# Create an instance of the Distance class
obj = Distance()

# Create a thread for the low_distance function
t1 = Thread(target=low_distance, args=(obj,))
t1.start()

try:
    while True:
        # Get the distance measurement from the ultrasonic sensor
        distance = get_distance()

        # Check if the distance is within the valid range (20 to 400 cm)
        if distance > 20 and distance < 400:
            obj.l = distance
            print("Distance:", distance - 0.5, "cm")  # Offset the distance by 0.5 cm
        else:
            print("Out Of Range")
except KeyboardInterrupt:
    print("Goodbye!")
    GPIO.cleanup()
    exit()


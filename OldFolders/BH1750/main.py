import board
import adafruit_bh1750
from time import sleep


i2c = board.I2C()

sensor = adafruit_bh1750.BH1750(i2c)

try:
    while True:
        print(round(sensor.lux, 2), "lx")
        sleep(1)
except KeyboardInterrupt:
    # Handle the Ctrl+C keyboard interrupt gracefully
    print("Goodbye!")


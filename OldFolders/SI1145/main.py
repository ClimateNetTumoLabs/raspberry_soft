import time
import board
import busio
from adafruit_si1145 import SI1145

i2c = busio.I2C(board.SCL, board.SDA)

sensor = SI1145(i2c)

while True:
    vis, ir = sensor.als

    uv = sensor.uv_index

    print("Visible Light:", vis)
    print("Infrared Light:", ir)
    print("UV Index:", uv)

    print("\n" + ("#" * 50) + "\n")

    time.sleep(1)

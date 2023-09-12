import serial
from time import sleep


ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate=9600,
    timeout=1
)


request = bytes([0xFF, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79])

try:
    while True:
        ser.write(request)

        response = ser.read(9)
        res = list(response)
        print(res)
        print(res[2] * 256 + res[3])
        sleep(1)
except Exception as e:
    print(e)
finally:
    ser.close()

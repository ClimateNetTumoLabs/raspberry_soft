from pms5003 import PMS5003


print("\nPress Ctrl+C to exit!\n")

# Initialize the PMS5003 sensor object with required configurations
pms5003 = PMS5003(
    device='/dev/ttyS0',   # The device port for the PMS5003 sensor
    baudrate=9600,         # The baud rate for communication with the sensor
    pin_enable=27,         # The GPIO pin used to enable the sensor
    pin_reset=22           # The GPIO pin used to reset the sensor
)

try:
    while True:
        data = pms5003.read()
        print(data)

except KeyboardInterrupt:
    # Handle the Ctrl+C keyboard interrupt gracefully
    print("Goodbye!")


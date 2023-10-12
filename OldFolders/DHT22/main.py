import time
import board
import adafruit_dht


# Initialize the DHT22 sensor on pin D27
dhtDevice = adafruit_dht.DHT22(board.D27)

while True:
    try:
        # Read temperature and humidity from the DHT22 sensor
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity

        # Display the temperature and humidity readings
        print(f"Temperature: {temperature}C    Humidity: {humidity}")

        # Wait for 2 seconds before taking the next reading
        time.sleep(2)

    except RuntimeError as error:
        # Handle runtime errors from the sensor (e.g., communication issues)
        print(error.args[0])

        # Wait for 2 seconds before retrying the reading
        time.sleep(2)
        continue

    except KeyboardInterrupt:
        # Handle the Ctrl+C keyboard interrupt gracefully
        print("Goodbye!")

        # Exit the DHT22 sensor to clean up and release resources
        dhtDevice.exit()

    except Exception as error:
        # Handle other unexpected exceptions (if any)
        print(error)

        # Exit the DHT22 sensor to clean up and release resources
        dhtDevice.exit()


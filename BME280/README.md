# BME280 Sensor Data Logger

This Python program is designed to read data from the BME280 sensor and display the measured values of **temperature**, **pressure**, **humidity**, and **altitude above sea level**. The program uses the *smbus2* and *bme280* libraries to communicate with the sensor and retrieve data.

## Installation

1. Clone the repository to your device:
   ```
   git clone https://github.com/ClimateNetTumoLabs/AramSamoHovo.git
   ```
   ```
   cd AramSamoHovo/
   ```

2. Checkout to branch **hovo**, and go to folder **BME280**
   ```
   git checkout hovo
   ```
   ```
   cd BME280/
   ```

3. It is recommended to create a virtual environment to isolate the project's dependencies:
   ```
   python3 -m venv venv
   ```

4. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```

5. Install the dependencies from the `requirements.txt` file:

   ```
   pip install -r requirements.txt
   ```

## Usage

To use this program, follow these steps:

1. Connect the BME280 sensor to your Raspberry Pi (or compatible platform) using the appropriate connections.

2. Make sure the hardware is properly set up and the sensor is connected to the I2C bus.

3. Run the Python script main.py using the following command:

   ```
   python main.py
   ```
The program will continuously display the measured values of temperature, pressure, humidity, and calculated altitude above sea level in a loop.


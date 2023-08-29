# DHT22 Sensor Data Logger

This Python program reads temperature and humidity data from the **DHT22** sensor and displays the measured values in a loop. The program utilizes the *adafruit_dht* library to interface with the **DHT22** sensor.

## Installation

1. Clone the repository to your device:
   ```
   git clone https://github.com/ClimateNetTumoLabs/AramSamoHovo.git
   ```
   ```
   cd AramSamoHovo/
   ```

2. Checkout to branch **hovo**, and go to folder **DHT22**
   ```
   git checkout hovo
   ```
   ```
   cd DHT22/
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

1. Ensure the DHT22 sensor is connected to the correct GPIO pin (D27 or the pin you specified in the program).

2. Run the Python script main.py using the following command:

   ```
   python main.py
   ```
The program will continuously display the measured values of temperature (in Celsius) and humidity.


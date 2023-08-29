# PMS5003 Sensor Data Logger

This Python script continuously reads data from the **PMS5003** sensor and prints all the data values. The **PMS5003** sensor is a particulate matter (PM) sensor that measures PM1.0, PM2.5, and PM10 concentrations in the air.

## Installation

1. Clone the repository to your device:
   ```
   git clone https://github.com/ClimateNetTumoLabs/AramSamoHovo.git
   ```
   ```
   cd AramSamoHovo/
   ```

2. Checkout to branch **hovo**, and go to folder **PMS5003**
   ```
   git checkout hovo
   ```
   ```
   cd PMS5003/
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

1. Ensure the PMS5003 sensor is correctly connected to the specified serial port (`/dev/ttyS0` or your specified port).`

2. Run the Python script main.py using the following command:

   ```
   python main.py
   ```
The script will continuously read data from the PMS5003 sensor and print all the data values in the console.


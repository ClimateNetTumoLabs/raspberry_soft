# AllInOne Sensor Data Viewer

The **AllInOne** folder in this repository contains a project that collects data from four different sensors (*BH1750*, *BME280*, *JSN-SR04T*, and *PMS5003*) and displays the collected data on the screen.

## Installation

1. Clone the repository to your device:
   ```
   git clone https://github.com/ClimateNetTumoLabs/AramSamoHovo.git
   ```
   ```
   cd AramSamoHovo/
   ```

2. Checkout to branch **hovo**, and go to folder **AllInOne**
   ```
   git checkout hovo
   ```
   ```
   cd AllInOne/
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



## Project Structure

The **AllInOne** folder contains the following files:

- `LightSensorBH1750.py`: This file contains the class to work with the **BH1750** light sensor.
- `TPHSensorBME280.py`: This file contains the class to work with the **BME280** temperature, humidity, and pressure sensor.
- `UltrasonicSensorJSN_SR04T.py`: This file contains the class to work with the **JSN-SR04T** ultrasonic distance sensor.
- `AirQualitySensorPMS5003.py`: This file contains the class to work with the **PMS5003** air quality sensor.
- `main.py`: The main file of the project that brings together all the sensor classes and manages their interactions to display data on the screen.

## Usage

To run the project and view the sensor data on the screen, make sure the virtual environment is activated (see installation steps) and execute the following command from the **AllInOne** folder:

```
python main.py
```

The `main.py` file will load and initialize all the sensor classes, collect data from the sensors, and display the data on the screen.

# BH1750 Sensor Data Viewer

The "BH1750" folder in this repository contains a program for measuring light levels using the BH1750 light sensor.


## Installation

1. Clone the repository to your device:
   ```
   git clone https://github.com/ClimateNetTumoLabs/AramSamoHovo.git
   ```
   ```
   cd AramSamoHovo/
   ```

2. Checkout to branch **hovo**, and go to folder **BH1750**
   ```
   git checkout hovo
   ```
   ```
   cd BH1750/
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

1. The `main.py` file is a simple program that performs light level measurements using default settings.

   Run the `main.py` file to start light level measurements:
   ```
   python main.py
   ```

2. The `with_modes.py` file provides more advanced functionalities and settings for light level measurements using the BH1750 sensor. It allows you to customize the types of measurements and other settings.

   To run the program with customizable modes, execute the following command:
   ```
   python with_modes.py
   ```

   ### Available Modes

   The `with_modes.py` file supports the following modes:

   - `ONE_TIME_HIGH_RES_MODE`: One-time high-resolution measurement mode.
   - `ONE_TIME_HIGH_RES_MODE_2`: One-time high-resolution mode 2 (different sensitivity range).
   - `ONE_TIME_LOW_RES_MODE`: One-time low-resolution measurement mode.
   - `CONTINUOUS_HIGH_RES_MODE`: Continuous high-resolution measurement mode.
   - `CONTINUOUS_HIGH_RES_MODE_2`: Continuous high-resolution mode 2 (different sensitivity range).
   - `CONTINUOUS_LOW_RES_MODE`: Continuous low-resolution measurement mode.

To change the measurement mode, modify the `MODE` variable in the `with_modes.py` file.

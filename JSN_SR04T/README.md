# JSN_SR04T Sensor Data Logger

This Python program is designed to read data from the **JSN_SR04T** ultrasonic distance sensor and display the measured distance to objects. The program uses the `RPi.GPIO`, `time`, and `threading` libraries to communicate with the sensor and control a buzzer based on distance thresholds.

## Installation

1. Clone the repository to your device:
   ```
   git clone https://github.com/ClimateNetTumoLabs/AramSamoHovo.git
   ```
   ```
   cd AramSamoHovo/
   ```

2. Checkout to branch **hovo**, and go to folder **JSN_SR04T**
   ```
   git checkout hovo
   ```
   ```
   cd JSN_SR04T/
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

1. Connect the JSN_SR04T ultrasonic distance sensor to the GPIO pins of your Raspberry Pi, following the appropriate instructions for your sensor.

2. Run the Python script main.py using the following command:

   ```
   python parktronic.py
   ```
The program will start measuring distances using the ultrasonic sensor and continuously display the results on the console. You will be able to observe the measured distances and see changes as objects move closer to or farther away from the sensor.

Additionally, the program will adjust the frequency of the buzzer based on the measured distance. The buzzer will be activated with a certain frequency depending on the distance thresholds set in the `low_distance` function. As the measured distance falls within different ranges, the buzzer frequency will change accordingly.

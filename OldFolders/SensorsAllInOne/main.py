from LightSensorBH1750 import LightSensor
from AirQualitySensorPMS5003 import AirQualitySensor
from TPHSensorBME280 import TPHSensor
from UltrasonicSensorJSN_SR04T import UltrasonicSensor


def main(light_obj, tph_obj, air_quality_obj, distance_obj):
    """
    Reads data from various sensors and combines them into a dictionary called data.

    Parameters:
        light_obj (LightSensor): Object for working with the light sensor.
        tph_obj (TPHSensor): Object for working with the temperature, humidity, and pressure sensor.
        air_quality_obj (AirQualitySensor): Object for working with the air quality sensor.
        distance_obj (UltrasonicSensor): Object for working with the ultrasonic distance sensor.

    Returns:
        dict: A dictionary containing data read from various sensors.
    """
    
    # Use an empty dictionary to store the data.
    data = {}
    
    # Read data from the light sensor and store it in the data dictionary.
    data["Light"] = light_obj.read_data()
    
    # Read data from the temperature, humidity, and pressure sensor and update the data dictionary.
    tph_data = tph_obj.read_data()
    data.update(tph_data)

    # Read data from the air quality sensor and update the data dictionary.
    air_quality_data = air_quality_obj.read_data()
    data.update(air_quality_data)
    
    # Read data from the ultrasonic distance sensor and store it in the data dictionary.
    data["Distance"] = distance_obj.read_data()
    
    # Return the dictionary with data read from various sensors.
    return data


if __name__ == "__main__":
    # Create objects for each sensor.
    light_obj = LightSensor() 
    tph_obj = TPHSensor()
    air_quality_obj = AirQualitySensor()
    distance_obj = UltrasonicSensor()

    # In an infinite loop, read data from the sensors and print it on the screen.
    while True:
        data = main(light_obj, tph_obj, air_quality_obj, distance_obj)

        for key, value in data.items():
            print(f"{key}: {value}")

        print("\n" + ("#" * 50) + "\n")


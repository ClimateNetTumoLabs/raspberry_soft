import time
from datetime import datetime
from read_sensors import ReadSensor
from network_check import check_network
from MQTT_Sender import MQTTClient
from LocalDB import LocalDatabase
from logger_config import *


def main(deviceID="device5"):
    # time.sleep(30)

    sensor_reader = ReadSensor(measuring_time=60)

    mqtt_client = MQTTClient(deviceID=deviceID)
    local_db = LocalDatabase(deviceID=deviceID)

    local = False

    while True:
        try:
            data = sensor_reader.collect_data()
            logging.info(f"{data}")
            
            insert_data = tuple([datetime.now().isoformat()] + list(data.values()))

            if check_network():
                if local:
                    local_data = local_db.get_data()
                    local_data.append(insert_data)
                    local_db.drop_table()

                    mqtt_client.send_data(local_data)
                    local = False
                    logging.info("Send local data & current data to RDS")
                else:
                    mqtt_client.send_data([insert_data])
                    logging.info("Send current data to RDS")
            else:
                local = True
                local_db.insert_data(insert_data)
                logging.info("Send current data to local DB")

        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main("device5")

"""
├── LocalDB
│   ├── config.py
│   └── __init__.py
├── MQTT_Sender
│   ├── certificate.pem.crt
│   ├── __init__.py
│   ├── private.pem.key
│   ├── public.pem.key
│   └── rootCA.pem
├── Sensors
│   ├── AirQualitySensorPMS5003.py
│   ├── CO2SensorMH_Z16.py
│   ├── __init__.py
│   ├── LightSensorBH1750.py
│   ├── PMS5003_library
│   │   └── __init__.py
│   └── TPHSensorBME280.py
├── WeatherMeterSensors
│   ├── directions_config.json
│   ├── __init__.py
│   ├── RainSensor.py
│   ├── WindDirectionSensor.py
│   └── WindSpeedSensor.py
│
├── logger_config.py
├── main.py
├── network_check.py
├── parsing.log
├── read_sensors.py
├── requirements.txt

"""
import pytz
from datetime import datetime
from read_sensors import ReadSensor
from network_check import check_network
from MQTT_Sender import MQTTClient
from logger_config import *


if __name__ == "__main__":
    check_network()

    sensor_reader = ReadSensor(measuring_time=60)
    mqtt_client = MQTTClient()

    timezone = pytz.timezone('Asia/Yerevan')

    while True:
        try:
            data = sensor_reader.collect_data()
            logging.info(f"{data}")
            
            for key, value in data.items():
                print(key, " -> ", value)
            
            print("\n" + ("#" * 50) + "\n")
            
            insert_data = [datetime.now(tz=timezone).isoformat()] + list(data.values())

            mqtt_client.send_data("device4", insert_data)
        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)

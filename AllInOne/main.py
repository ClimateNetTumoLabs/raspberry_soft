from read_sensors import ReadSensor
from network_check import check_network
from MQTT_Sender import MQTTClient
from logger_config import *


if __name__ == "__main__":
    check_network()

    sensor_reader = ReadSensor()
    # mqtt_client = MQTTClient()

    while True:
        try:
            data = sensor_reader.collect_data()
            logging.info(f"{data}")
            # mqtt_client.send_data("device1", average_lst)
        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)

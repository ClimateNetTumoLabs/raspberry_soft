import time
from datetime import datetime
from read_sensors import ReadSensor
from network_check import check_network
from MQTT_Sender import MQTTClient
from LocalDB import LocalDatabase
from logger_config import *


def main(deviceID):
    # time.sleep(30)

    sensor_reader = ReadSensor(measuring_time=60)
    mqtt_client = MQTTClient(deviceID=deviceID)
    local_db = LocalDatabase(deviceID=deviceID)

    local = False

    while True:
        try:
            data = sensor_reader.get_data()

            logging.info("Data collection completed.")
            logging.info(f"Collected data -> {data}")
            
            insert_data = tuple([datetime.now().isoformat()] + list(data.values()))

            if check_network():
                if local:
                    logging.info("Send local & current data to RDS")
                    local_data = local_db.get_data()
                    local_data.append(insert_data)
                    local_db.drop_table()
                    print(local_data)
                    mqtt_client.send_data(local_data)
                    local = False
                else:
                    logging.info("Send current data to RDS")
                    mqtt_client.send_data([insert_data])
            else:
                local = True
                local_db.insert_data(insert_data)
                logging.info("Send current data to local DB")

        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main("device5")

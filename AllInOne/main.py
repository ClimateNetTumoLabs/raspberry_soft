import pytz
import time
from datetime import datetime
from read_sensors import ReadSensor
from network_check import check_network
from MQTT_Sender import MQTTClient
from LocalDB import LocalDatabase
from logger_config import *


def main():
    time.sleep(30)

    sensor_reader = ReadSensor(measuring_time=60)
    mqtt_client = MQTTClient()
    local_db = LocalDatabase()

    local = False

    while True:
        try:
            data = sensor_reader.collect_data()
            logging.info(f"{data}")
            
            for key, value in data.items():
                print(key, " -> ", value)
            
            print("\n" + ("#" * 50) + "\n")
            
            insert_data = tuple([datetime.now().isoformat()] + list(data.values()))

            if check_network():
                if local:
                    local_data = local_db.get_data("device4")
                    local_data.append(insert_data)

                    mqtt_client.send_data("device4", local_data)
                    local_db.drop_table("device4")
                    local = False
                else:
                    mqtt_client.send_data("device4", [insert_data])
            else:
                local = True
                local_db.insert_data("device4", insert_data)
                

        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
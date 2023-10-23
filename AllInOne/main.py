from datetime import datetime
from read_sensors import ReadSensor
from network_check import check_network
from MQTT_Sender import MQTTClient
from LocalDB import LocalDatabase
from logger_config import *
from scripts import update_time_from_ntp, split_data, chmod_tty


DEVICE_ID = 7


def main(deviceID):
    """
    Main function for ClimateNet data collection and transmission.

    This function collects sensor data, sends it to AWS RDS through MQTT,
    or stores it locally when there is no internet connection.

    Args:
        deviceID (str): The unique identifier of the device.

    Returns:
        None
    """

    sensor_reader = ReadSensor()
    mqtt_client = MQTTClient(deviceID=deviceID)
    local_db = LocalDatabase(deviceID=deviceID)
    local = False

    while True:
        try:
            data = sensor_reader.get_data()

            logging.info("Data collection completed.")
            logging.info(f"Collected data -> {data}")
            
            insert_data = tuple([datetime.now().isoformat()] + list(data.values()))

            if not check_network():
                local = True
                local_db.insert_data(insert_data)
                logging.info("Send current data to local DB")
            
            elif local:
                logging.info("Send local & current data to RDS")
                local_data = local_db.get_data()
                local_data.append(insert_data)

                splitted_data = split_data(insert_data)
                mqtt_res = True
                for lst in splitted_data:
                    mqtt_res = mqtt_client.send_data(lst)
                    if not mqtt_res:
                        mqtt_res = False
                        break

                if mqtt_res:
                    local_db.drop_table()
                    local = False
                else:
                    logging.info("Send current data to local DB")
                    local_db.insert_data(insert_data)
                
            else:
                logging.info("Send current data to RDS")
                mqtt_client.send_data([insert_data])

        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    logging.info("Program started")
    update_time_from_ntp()
    chmod_tty()
    main(f"device{DEVICE_ID}")

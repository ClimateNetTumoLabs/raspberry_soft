import time
import sys
import math
import subprocess
from datetime import datetime
from read_sensors import ReadSensor
from network_check import check_network
from MQTT_Sender import MQTTClient
from LocalDB import LocalDatabase
from logger_config import *


DEVICE_ID = 5


def chmod_tty():
    command = 'sudo chmod 777 /dev/ttyS0'

    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logging.info(f"Successfully changed mode for /dev/ttyS0")
        else:
            logging.error(f"Error while changing mode for /dev/ttyS0: {result.stderr}")
    except Exception as e:
        logging.error(f"Error while changing mode for /dev/ttyS0 {str(e)}")
        raise


def get_quantity(data_lst):
    size_in_bytes = sys.getsizeof(data_lst)
    size = 256 * 1024 * 1024

    return math.ceil(size_in_bytes / size)


def split_data(data_lst):
    quantity = get_quantity(data_lst)
    avg = len(data_lst) // quantity
    remainder = len(data_lst) % quantity
    
    result = []
    start = 0
    for i in range(quantity):
        if i < remainder:
            end = start + avg + 1
        else:
            end = start + avg
        result.append(data_lst[start:end])
        start = end

    return result


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
    time.sleep(30)
    #TODO: Change tine.sleep function to normal function that can check internet and request real time
    chmod_tty()
    main(f"device{DEVICE_ID}")

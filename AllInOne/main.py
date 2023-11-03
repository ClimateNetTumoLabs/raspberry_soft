from datetime import datetime
from read_sensors import ReadSensor
from network_check import check_network
from MQTT_Sender import MQTTClient
from LocalDB import LocalDatabase
from logger_config import *
from scripts import update_time_from_ntp, split_data, chmod_tty


DEVICE_ID = 7


class DataSaver:
    def __init__(self, deviceID):
        self.mqtt_client = MQTTClient(deviceID=deviceID)
        self.local_db = LocalDatabase(deviceID=deviceID)

        self.local = False

    def __save_local(self, data):
        logging.info('Send current data to local DB')
        self.local_db.insert_data(data)
    
    def __get_local(self, data):
        local_data = self.local_db.get_data()
        local_data.append(data)

        splitted_data = split_data(local_data)
        return splitted_data
    
    def __save_rds(self, data, local = False):
        if local:
            logging.info('Send local & current data to RDS')
            
            mqtt_res = True
            for lst in self.__get_local(data):
                mqtt_res = self.mqtt_client.send_data(lst)
                if not mqtt_res:
                    break

            if mqtt_res:
                self.local_db.drop_table()
                return True
            else:
                return False

        else:
            logging.info('Send current data to RDS')
            mqtt_res = self.mqtt_client.send_data([data])

            return mqtt_res
    
    def save(self, data):
        if not check_network():
            self.local = True
            self.__save_local(data)
        
        else:
            res = self.__save_rds(data, self.local)

            if res:
                self.local = False
            else:
                self.__save_local(data)


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
    dataSaver = DataSaver(deviceID)

    while True:
        try:
            data = sensor_reader.collect_data()

            logging.info("Data collection completed.")
            logging.info(f"Collected data -> {data}")
            
            insert_data = tuple([datetime.now().isoformat()] + list(data.values()))

            dataSaver.save(insert_data)
        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    update_time_from_ntp()
    chmod_tty()
    logging.info("Program started")
    main(f"device{DEVICE_ID}")

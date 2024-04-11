from .mqtt_client import MQTTClient
from logger_config import logging
from scripts.data_splitter import split_data
from scripts.network_checker import check_network


class DataHandler:
    def __init__(self, device_id, local_database) -> None:
        """
        Initializes a DataHandler instance.

        Returns:
            None
        """
        self.deviceID = f"device{device_id}"
        self.mqtt_client = MQTTClient(deviceID=self.deviceID)
        self.local_db = local_database

        self.local = False

    def __save_local(self, data: dict) -> None:
        """
        Saves data to the local database.

        Args:
            data (dict): The data to be saved.

        Returns:
            None
        """
        logging.info('Send current data to local DB')
        self.local_db.insert_data(data)

    def __get_local(self) -> list:
        """
        Retrieves data from the local database.

        Returns:
            list: A list containing the retrieved data.
        """
        local_data = self.local_db.get_data()

        return local_data

    def __send_mqtt(self, data: dict, local=False) -> bool:
        """
        Sends data to the MQTT broker.

        Args:
            data (dict): The data to be sent.
            local (bool): Indicates whether to send local data along with the current data.

        Returns:
            bool: True if the data is successfully sent, False otherwise.
        """
        if local:
            logging.info('Send local & current data to RDS')

            mqtt_res = True

            all_data = self.__get_local()
            all_data.append(data)

            splitted_data = split_data(all_data)

            for elem in splitted_data:
                mqtt_res = self.mqtt_client.send_data(elem)
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

    def send_only_local(self):
        """
        Sends only local data to the remote server.

        Returns:
            bool: True if the local data is successfully sent, False otherwise.
        """
        logging.info('Send local data to RDS')
        mqtt_res = True

        data = self.__get_local()
        splitted_data = split_data(data)

        for elem in splitted_data:
            mqtt_res = self.mqtt_client.send_data(elem)
            if not mqtt_res:
                break

        if mqtt_res:
            self.local_db.drop_table()
            return True
        else:
            self.local = True
            return False

    def save(self, data: dict) -> None:
        """
        Saves data based on the availability of the network.

        Args:
            data (dict): The data to be saved.

        Returns:
            None
        """
        if not check_network():
            self.local = True
            self.__save_local(data)

        else:
            res = self.__send_mqtt(data, self.local)

            if res:
                self.local = False
            else:
                self.__save_local(data)

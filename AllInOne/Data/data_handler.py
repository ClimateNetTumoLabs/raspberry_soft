"""
    Data handling module for managing sensor data storage and transmission.

    This module provides a class, DataHandler, for handling the storage and transmission of sensor data.
    The class includes methods for saving data to a local database and sending it to an MQTT broker.

    Class Docstring:
    ----------------
    DataHandler:
        Manages the storage and transmission of sensor data.

    Constructor:
        Initializes a DataHandler object, creates instances of LocalDatabase and MQTTClient.

    Class Attributes:
        deviceID (str): Identifier for the device.
        mqtt_client (MQTTClient): MQTT Client for sending data to an MQTT broker.
        local_db (LocalDatabase): Local database for storing sensor data.
        local (bool): Flag indicating whether the device is currently operating in local mode.

    Methods:
        __init__(self):
            Initializes a DataHandler object.

        __save_local(self, data: dict):
            Saves data to the local database.

        __get_local(self, data: dict) -> list:
            Retrieves local data and combines it with the current data.

        __send_mqtt(self, data: dict, local=False) -> bool:
            Sends data to the MQTT broker.

        save(self, data: dict):
            Saves sensor data either locally or to an MQTT broker based on network availability.

    Module Usage:
    -------------
    To use this module, create an instance of the DataHandler class.
    Call the save() method with sensor data as an argument to manage storage and transmission.
"""

from .LocalDB import LocalDatabase
from .MQTT_Sender import MQTTClient
from logger_config import *
from Scripts import split_data, check_network
from config import DEVICE_ID


class DataHandler:
    """
    Manages the storage and transmission of sensor data.

    Attributes:
        deviceID (str): Identifier for the device.
        mqtt_client (MQTTClient): MQTT Client for sending data to an MQTT broker.
        local_db (LocalDatabase): Local database for storing sensor data.
        local (bool): Flag indicating whether the device is currently operating in local mode.
    """
    def __init__(self) -> None:
        """
        Initializes a DataHandler object, creates instances of LocalDatabase and MQTTClient.
        """
        self.deviceID = f"device{DEVICE_ID}"
        self.mqtt_client = MQTTClient(deviceID=self.deviceID)
        self.local_db = LocalDatabase(deviceID=self.deviceID)

        self.local = False

    def __save_local(self, data: dict) -> None:
        """
        Saves data to the local database.

        Args:
            data (dict): Sensor data to be saved locally.
        """
        logging.info('Send current data to local DB')
        self.local_db.insert_data(data)

    def __get_local(self) -> list:
        """
        Retrieves local data and combines it with the current data.

        Args:
            data (dict): Current sensor data.

        Returns:
            list: A list of tuples representing rows of data, each tuple includes timestamp and various sensor readings.
        """
        local_data = self.local_db.get_data()
        
        return local_data

    def __send_mqtt(self, data: dict, local=False) -> bool:
        """
        Sends data to the MQTT broker.

        Args:
            data (dict): Sensor data to be sent.
            local (bool): Flag indicating whether the data includes local data.

        Returns:
            bool: True if the data is sent successfully, False otherwise.
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
        Saves sensor data either locally or to an MQTT broker based on network availability.

        Args:
            data (dict): Sensor data to be saved.
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

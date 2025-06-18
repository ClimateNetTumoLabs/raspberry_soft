from logger_config import logging
from scripts.data_splitter import split_data


# Don't import network_checker since we're bypassing it


class DataHandler:
    """
    Handles data operations including saving to a local database and sending data via MQTT.

    Attributes:
        mqtt_client (Any): The MQTT client instance.
        local_db (Any): The local database instance.
        local (bool): Indicates whether the data should be saved locally.
    """

    def __init__(self, mqtt_client, local_database) -> None:
        """
        Initializes the DataHandler instance.

        Args:
            mqtt_client: The MQTT client instance.
            local_database: The local database instance.
        """
        self.mqtt_client = mqtt_client
        self.local_db = local_database
        self.local = False

    def __save_local(self, data: dict) -> None:
        """
        Saves the data to the local database.

        Args:
            data (dict): The data to be saved.
        """
        try:
            logging.info('SAVING DATA TO LOCAL DATABASE')
            self.local_db.insert_data(data)
            logging.info('DATA SUCCESSFULLY SAVED TO LOCAL DATABASE')
        except Exception as e:
            logging.error(f"Error saving data to local DB: {str(e)}", exc_info=True)

    def __get_local(self) -> list:
        """
        Retrieves data from the local database.

        Returns:
            list: A list of dictionaries containing the local data.
        """
        local_data = self.local_db.get_data()
        return local_data

    def __send_mqtt(self, data: dict) -> bool:
        """
        Attempts to send data via MQTT. Will fail fast if not connected.

        Args:
            data (dict): The data to be sent.

        Returns:
            bool: True if data was sent successfully, False otherwise.
        """
        # Check if MQTT client is connected before trying to send
        if not self.mqtt_client.client.is_connected():
            logging.info("MQTT client not connected - skipping send attempt")
            return False

        if self.local_db.get_count():
            logging.info('Send local & current data to RDS')

            mqtt_res = True

            all_data = self.__get_local()
            all_data.append(data)

            splitted_data = split_data(all_data)

            for elem in splitted_data:
                mqtt_res = self.mqtt_client.send_data(elem)
                if not mqtt_res:
                    logging.error("MQTT send failed")
                    break

            if mqtt_res:
                self.local_db.drop_table()
                return True
            else:
                return False

        else:
            logging.info('Send current data to RDS')
            mqtt_res = self.mqtt_client.send_data([data])

            if not mqtt_res:
                logging.error("MQTT send failed")

            return mqtt_res

    def send_only_local(self) -> bool:
        """
        Sends only the local data via MQTT.

        Returns:
            bool: True if data was sent successfully, False otherwise.
        """
        # Quick check if MQTT client is connected
        if not self.mqtt_client.client.is_connected():
            logging.info("MQTT client not connected - not sending local data")
            self.local = True
            return False

        logging.info('Send local data to RDS')
        mqtt_res = True

        data = self.__get_local()
        splitted_data = split_data(data)

        for elem in splitted_data:
            mqtt_res = self.mqtt_client.send_data(elem)
            if not mqtt_res:
                logging.error("MQTT send failed")
                break

        if mqtt_res:
            self.local_db.drop_table()
            return True
        else:
            self.local = True
            return False

    def save(self, data: dict) -> None:
        """
        Saves data, trying MQTT first and falling back to local storage if MQTT fails.
        Does not use network_checker at all.

        Args:
            data (dict): The data to be saved.
        """
        # Try to send via MQTT first
        try:
            logging.info("Attempting to send data via MQTT")
            res = self.__send_mqtt(data)
            if not res:
                logging.info("MQTT send failed - saving to local database")
                self.__save_local(data)
        except Exception as e:
            logging.error(f"Exception during MQTT send: {str(e)}")
            logging.info("Exception during MQTT - saving to local database")
            self.__save_local(data)
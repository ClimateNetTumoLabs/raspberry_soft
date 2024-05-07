"""Main module for collecting sensor data and storing it using a data handler.

This module orchestrates the collection of sensor data using the ReadSensors class,
and stores the collected data using the DataHandler class. The main function continuously
collects sensor data in a loop and saves it using the DataHandler.

The program first checks if there is any existing data in the local database. If there is,
it sends this data to a designated destination using the DataHandler's send_only_local method.

The sensor data is collected using the collect_data method of the ReadSensors class,
and the collected data is logged using the Python logging module.

The collected data is then augmented with a timestamp representing the time of collection,
formatted as an ISO 8601 string, and stored using the save method of the DataHandler class.

In case of any exceptions during execution, error messages are logged along with exception details.

Attributes:
    sensor_reader (ReadSensors): An instance of the ReadSensors class responsible for reading sensor data.
    dataHandler (DataHandler): An instance of the DataHandler class responsible for handling data storage.

Functions:
    main(): The main function orchestrating the collection and storage of sensor data.

Example:
    To execute the program, run the script directly:

    $ python main.py
"""

from datetime import datetime

import config
from data.data_handler import DataHandler
from data.local_db import LocalDatabase
from data.mqtt_client import MQTTClient
from sensors.read_sensors import ReadSensors
from logger_config import logging
from scripts.time_updater import update_time
from scripts.change_permissions import chmod_tty


def main():
    """Main function for collecting and storing sensor data."""
    sensor_reader = ReadSensors()
    local_database = LocalDatabase(deviceID=config.DEVICE_ID,
                                   host=config.LOCAL_DB_HOST,
                                   username=config.LOCAL_DB_USERNAME,
                                   password=config.LOCAL_DB_PASSWORD,
                                   db_name=config.LOCAL_DB_DB_NAME)
    mqtt_client = MQTTClient(deviceID=config.DEVICE_ID)

    dataHandler = DataHandler(mqtt_client=mqtt_client, local_database=local_database)

    # Check if there is any existing data in the local database
    if dataHandler.local_db.get_count():
        # Send existing data to designated destination
        dataHandler.send_only_local()

    # Continuous loop for collecting and storing sensor data
    while True:
        try:
            # Collect sensor data
            data = sensor_reader.collect_data()

            # Log data collection completion and collected data
            logging.info("Data collection completed.")
            logging.info(f"Collected data -> {data}")

            # Add timestamp to collected data
            data['time'] = datetime.now().isoformat()

            # Save collected data
            dataHandler.save(data)
        except Exception as e:
            # Log errors during execution
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # Perform necessary setup tasks
    update_time()
    chmod_tty()

    # Log program start
    logging.info("Program started")

    # Execute main function
    main()

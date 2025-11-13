from datetime import datetime

import config
from data.data_handler import DataHandler
from data.local_db import LocalDatabase
from data.mqtt_client import MQTTClient
from logger_config import logging
from scripts.change_permissions import chmod_tty
from scripts.time_updater import update_time
from sensors.read_sensors import ReadSensors


def main() -> None:
    """
    Main function to initialize sensors, databases, MQTT client, and continuously collect and store sensor data.

    Raises:
        Exception: If any unexpected error occurs during execution.
    """
    # Initialize sensors
    logging.info("Initializing sensors...")
    sensor_reader = ReadSensors()

    # Initialize local database
    logging.info("Initializing local database...")
    local_database = LocalDatabase(deviceID=config.DEVICE_ID,
                                   db_name=config.LOCAL_DB_DB_NAME)

    # Initialize MQTT client (may fail if offline)
    logging.info("Initializing MQTT client...")
    mqtt_client = MQTTClient(deviceID=config.DEVICE_ID)

    # Initialize data handler
    logging.info("Initializing data handler...")
    dataHandler = DataHandler(mqtt_client=mqtt_client, local_database=local_database)

    # Check if there is any existing data in the local database
    local_data_count = dataHandler.local_db.get_count()
    if local_data_count:
        logging.info(f"Found {local_data_count} records in local database - attempting to send")
        # Send existing data to designated destination
        dataHandler.send_only_local()

    # Continuous loop for collecting and storing sensor data
    logging.info("Starting main data collection loop")
    while True:
        try:
            # Collect sensor data
            data = sensor_reader.collect_data()

            # Log data collection completion and collected data
            logging.info("Data collection completed.")
            logging.info(f"Collected data -> {data}")

            # Add timestamp to collected data
            data['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Save collected data
            logging.info("Saving data...")
            dataHandler.save(data)
            logging.info("Data saved. Continuing to next collection cycle.")

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
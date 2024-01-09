from datetime import datetime
from Sensors import ReadSensors
from Data import DataHandler
from logger_config import *
from Scripts import update_time_from_ntp, chmod_tty


def main():
    # Initialize sensor reader and data handler
    sensor_reader = ReadSensors()
    dataHandler = DataHandler()

    if dataHandler.local_db.get_count():
        dataHandler.send_only_local()

    # Main loop for continuous data collection and handling
    while True:
        try:
            # Collect sensor data
            data = sensor_reader.collect_data()

            # Log information about completed data collection
            logging.info("Data collection completed.")
            logging.info(f"Collected data -> {data}")

            # Add timestamp to collected data
            data['time'] = datetime.now().isoformat()

            # Save data using the data handler
            dataHandler.save(data)
        except Exception as e:
            # Log any errors that occur during execution
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    # Perform initial setup tasks before starting the main program
    update_time_from_ntp()
    chmod_tty()

    # Log the start of the program
    logging.info("Program started")

    # Start the main program
    main()

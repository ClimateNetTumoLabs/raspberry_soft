from datetime import datetime
from Sensors import ReadSensors
from DataSaver import DataSaver
from logger_config import *
from Scripts import update_time_from_ntp, chmod_tty


def main():
    """
    Main function for ClimateNet data collection and transmission.

    This function collects sensor data, sends it to AWS RDS through MQTT,
    or stores it locally when there is no internet connection.

    Args:
        deviceID (str): The unique identifier of the device.

    Returns:
        None
    """

    sensor_reader = ReadSensors()
    dataSaver = DataSaver()

    while True:
        try:
            data = sensor_reader.collect_data()

            logging.info("Data collection completed.")
            logging.info(f"Collected data -> {data}")

            data['time'] = datetime.now().isoformat()
            
            # insert_data = tuple([datetime.now().isoformat()] + list(data.values()))

            dataSaver.save(data)
        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)


if __name__ == "__main__":
    update_time_from_ntp()
    chmod_tty()
    logging.info("Program started")
    main()

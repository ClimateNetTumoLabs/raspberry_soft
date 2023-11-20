from datetime import datetime
from Sensors import ReadSensor
from DataSaver import DataSaver
from logger_config import *
from Scripts import update_time_from_ntp, chmod_tty


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

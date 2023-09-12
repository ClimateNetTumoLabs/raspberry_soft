import logging
from read_sensors import ReadSensor
from network_check import check_network
from db import Database

logging.basicConfig(filename='parsing.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == "__main__":
    check_network()

    sensor_reader = ReadSensor()
    db = Database()

    while True:
        try:
            data = sensor_reader.collect_data()
            logging.info(f"{data}")
            average_lst = sensor_reader.get_averages_list(data)
            logging.info(f"{average_lst}")
            db.insert_data(average_lst)
        except Exception as e:
            logging.error(f"Error occurred during execution: {str(e)}", exc_info=True)

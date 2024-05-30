from logger_config import logging
from scripts.data_splitter import split_data
from scripts.network_checker import check_network


class DataHandler:
    def __init__(self, mqtt_client, local_database) -> None:
        self.mqtt_client = mqtt_client
        self.local_db = local_database

        self.local = False

    def __save_local(self, data: dict) -> None:
        logging.info('Send current data to local DB')
        self.local_db.insert_data(data)

    def __get_local(self) -> list:
        local_data = self.local_db.get_data()
        return local_data

    def __send_mqtt(self, data: dict) -> bool:
        if self.local_db.get_count():
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
        if not check_network():
            self.__save_local(data)

        else:
            res = self.__send_mqtt(data)

            if not res:
                self.__save_local(data)

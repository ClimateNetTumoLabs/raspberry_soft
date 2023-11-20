from .LocalDB import LocalDatabase
from MQTT_Sender import MQTTClient
from logger_config import *
from Scripts import split_data, check_network

class DataSaver:
    def __init__(self, deviceID):
        self.mqtt_client = MQTTClient(deviceID=deviceID)
        self.local_db = LocalDatabase(deviceID=deviceID)

        self.local = False

    def __save_local(self, data):
        logging.info('Send current data to local DB')
        self.local_db.insert_data(data)
    
    def __get_local(self, data):
        local_data = self.local_db.get_data()
        local_data.append(data)

        splitted_data = split_data(local_data)
        return splitted_data
    
    def __send_mqtt(self, data, local = False):
        if local:
            logging.info('Send local & current data to RDS')
            
            mqtt_res = True
            for lst in self.__get_local(data):
                mqtt_res = self.mqtt_client.send_data(lst)
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
    
    def save(self, data):
        if not check_network():
            self.local = True
            self.__save_local(data)
        
        else:
            res = self.__send_mqtt(data, self.local)

            if res:
                self.local = False
            else:
                self.__save_local(data)
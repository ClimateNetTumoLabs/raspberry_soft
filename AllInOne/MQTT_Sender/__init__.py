import json
import ssl
import os
import time
import paho.mqtt.client as mqtt
from logger_config import *


class MQTTClient:
    def __init__(self, deviceID) -> None:
        self.client = mqtt.Client()
        self.client.tls_set(ca_certs=os.path.join(os.path.dirname(__file__), 'rootCA.pem'),
                            certfile=os.path.join(os.path.dirname(__file__), 'certificate.pem.crt'), 
                            keyfile=os.path.join(os.path.dirname(__file__), 'private.pem.key'), 
                            tls_version=ssl.PROTOCOL_SSLv23)
        self.client.tls_insecure_set(True)
        self.client.connect("a3b2v7yks3ewbi-ats.iot.us-east-1.amazonaws.com", 8883, 60)

        self.client.loop_start()

        self.deviceID = deviceID
    
    def send_data(self, data):
        if not self.client.is_connected():
            logging.info("Reconnecting to MQTT Broker")
            self.client.reconnect()
            
            is_connected = False

            t = time.time()
            while time.time() - t <= 15:
                if self.client.is_connected():
                    is_connected = True
                    logging.info("Connected to MQTT Broker")
                    break
                time.sleep(1)

            if not is_connected:
                logging.error("Failed to connect to MQTT Broker")
                return False
        
        message = {
            "device": self.deviceID,
            "data": data
        }

        message_json = json.dumps(message)
        logging.info(message_json)
        self.client.publish("raspberry/devices", message_json)
        
        return True

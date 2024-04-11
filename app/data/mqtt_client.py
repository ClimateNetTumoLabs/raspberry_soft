import json
import ssl
import os
import time
import socket
import paho.mqtt.client as mqtt
from logger_config import logging
from config import MQTT_BROKER_ENDPOINT, MQTT_TOPIC


class MQTTClient:
    def __init__(self, deviceID: str) -> None:
        """
        Initializes an MQTTClient instance.

        Args:
            deviceID (str): The unique identifier for the device associated with the MQTT client.

        Returns:
            None
        """
        self.client = mqtt.Client()
        self.client.tls_set(ca_certs=os.path.join(os.path.dirname(__file__), 'rootCA.pem'),
                            certfile=os.path.join(os.path.dirname(__file__), 'certificate.pem.crt'),
                            keyfile=os.path.join(os.path.dirname(__file__), 'private.pem.key'),
                            tls_version=ssl.PROTOCOL_SSLv23)
        self.client.tls_insecure_set(True)
        self.client.connect(MQTT_BROKER_ENDPOINT, 8883, 60)
        self.client.loop_start()
        self.deviceID = deviceID

    def send_data(self, data: list) -> bool:
        """
        Sends data to the MQTT broker.

        Args:
            data (list): The data to be sent.

        Returns:
            bool: True if the data is successfully sent, False otherwise.
        """
        if not self.client.is_connected():
            logging.info("Reconnecting to MQTT Broker...")
            try:
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
            except socket.timeout:
                logging.error("Error occurred during reconnecting to MQTT: socket.gaierror: [Errno -3] Temporary "
                              "failure in name resolution")
                return False
            except socket.gaierror:
                logging.error("Error occurred during reconnecting to MQTT: socket.timeout: _ssl.c:1106: The handshake "
                              "operation timed out")
                return False

        message = {
            "device": self.deviceID,
            "data": data
        }

        message_json = json.dumps(message)
        logging.info(f"MQTT Data: {str(message_json)}")

        self.client.publish(MQTT_TOPIC, message_json)

        return True

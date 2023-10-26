import json
import ssl
import os
import time
import socket
import paho.mqtt.client as mqtt
from logger_config import *


class MQTTClient:
    """
    Class for connecting to and publishing data to an MQTT broker.

    This class provides methods for connecting to an MQTT broker using secure TLS communication and publishing
    data to a specified topic.

    Args:
        deviceID (str): The unique identifier for the device connecting to the MQTT broker.

    Methods:
        send_data(self, data):
            Send data to the MQTT broker. Reconnects and retries if not connected.

    Attributes:
        client (paho.mqtt.client.Client): The MQTT client instance for communication.
        deviceID (str): The unique identifier for the device.

    """

    def __init__(self, deviceID) -> None:
        """
        Initialize the MQTTClient class.

        This method initializes the MQTTClient class, sets up the MQTT client with TLS security,
        and connects to the MQTT broker.

        Args:
            deviceID (str): The unique identifier for the device connecting to the MQTT broker.

        Returns:
            None
        """
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
        """
        Send data to the MQTT broker. Reconnects and retries if not connected.

        This method sends data to the MQTT broker, and if the client is not connected, it attempts to reconnect
        and then sends the data. It returns True if the data is sent successfully and False if there's an issue.

        Args:
            data: The data to send to the MQTT broker.

        Returns:
            bool: True if the data is sent successfully, False if there's an issue.
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
                logging.error("Error occurred during reconnecting to MQTT: socket.gaierror: [Errno -3] Temporary failure in name resolution")
                return False
            except socket.gaierror:
                logging.error("Error occurred during reconnecting to MQTT: socket.timeout: _ssl.c:1106: The handshake operation timed out")
                return False
        
        message = {
            "device": self.deviceID,
            "data": data
        }

        message_json = json.dumps(message)
        self.client.publish("raspberry/devices", message_json)
        
        return True

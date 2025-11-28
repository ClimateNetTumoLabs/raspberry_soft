import json
import os
import ssl
import time

import paho.mqtt.client as mqtt
from config import MQTT_BROKER_ENDPOINT, MQTT_TOPIC, DEVICE_ID
from logger_config import logging


class MQTTClient:
    def __init__(self, deviceID: str) -> None:

        self.client = mqtt.Client()
        self.client.tls_set(
            ca_certs=os.path.join(os.path.dirname(__file__), 'certificates/rootCA.pem'),
            certfile=os.path.join(os.path.dirname(__file__), 'certificates/certificate.pem.crt'),
            keyfile=os.path.join(os.path.dirname(__file__), 'certificates/private.pem.key'),
            tls_version=ssl.PROTOCOL_SSLv23
        )
        self.client.tls_insecure_set(True)

        # Try to connect, but don't block if it fails
        try:
            self.client.connect_async(MQTT_BROKER_ENDPOINT, 8883, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {str(e)}")

        self.deviceID = f"device{DEVICE_ID}"

    def send_data(self, data: list) -> bool:
        """
        Sends data to the MQTT broker - ONLY TRIES ONCE
        """
        if not self.client.is_connected():
            logging.info("MQTT client not connected, attempting to reconnect...")
            try:
                # ONLY TRY ONCE - no loop
                self.client.reconnect()
                time.sleep(1)  # Brief wait for connection

                if not self.client.is_connected():
                    logging.error("Failed to connect to MQTT Broker")
                    return False
                else:
                    logging.info("Connected to MQTT Broker")

            except Exception as e:
                logging.error(f"Error reconnecting to MQTT: {str(e)}")
                return False

        # If we reached here and still not connected, return False
        if not self.client.is_connected():
            return False

        message = {
            "device": self.deviceID,
            "data": data
        }

        message_json = json.dumps(message)
        logging.info(f"MQTT Data: {message_json}")

        # Publish with QoS 0 (fire and forget)
        self.client.publish(MQTT_TOPIC, message_json, qos=0)

        return True
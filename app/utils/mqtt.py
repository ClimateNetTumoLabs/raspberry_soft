import json
import os
import ssl
import threading
import time
from typing import List, Set

import paho.mqtt.client as mqtt
from config import MQTT_BROKER_ENDPOINT, MQTT_TOPIC, MQTT_ACK_TOPIC, DEVICE_ID
from logger_config import logging

CONNECT_TIMEOUT = 10
PUBLISH_TIMEOUT = 10


def _new_client() -> mqtt.Client:
    """paho 2.x requires an explicit callback API version; 1.x has no such argument."""
    try:
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    except AttributeError:
        return mqtt.Client()


class MQTTClient:
    def __init__(self, deviceID: str) -> None:
        self.deviceID = f"device{DEVICE_ID}"

        # Acks arrive on the paho network thread, so this set is shared state.
        self._acked = set()
        self._acked_lock = threading.Lock()
        self._ack_event = threading.Event()

        self.client = _new_client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.tls_set(
            ca_certs=os.path.join(os.path.dirname(__file__), 'certificates/rootCA.pem'),
            certfile=os.path.join(os.path.dirname(__file__), 'certificates/certificate.pem.crt'),
            keyfile=os.path.join(os.path.dirname(__file__), 'certificates/private.pem.key'),
            tls_version=ssl.PROTOCOL_SSLv23
        )
        self.client.tls_insecure_set(True)

        try:
            self.client.connect_async(MQTT_BROKER_ENDPOINT, 8883, 60)
            self.client.loop_start()
            self._wait_connected()
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {str(e)}")

    def _on_connect(self, client, userdata, flags, rc, *_):
        """Subscriptions do not survive a dropped session, so resubscribe on every connect."""
        if rc != 0:
            logging.error(f"MQTT connection refused (rc={rc})")
            return

        if MQTT_ACK_TOPIC:
            client.subscribe(MQTT_ACK_TOPIC, qos=1)
            logging.info(f"Subscribed to ack topic {MQTT_ACK_TOPIC}")
        else:
            logging.error("MQTT_ACK_TOPIC is not set, records can never be confirmed")

    def _on_message(self, client, userdata, msg):
        """Ack from the Lambda: these timestamps are committed in this device's table."""
        try:
            payload = json.loads(msg.payload.decode())
        except Exception as e:
            logging.error(f"Unparsable ack on {msg.topic}: {e}")
            return

        if payload.get("device") != self.deviceID:
            logging.warning(f"Ignoring ack addressed to {payload.get('device')}")
            return

        acked = payload.get("acked") or []

        with self._acked_lock:
            self._acked.update(acked)

        self._ack_event.set()
        logging.info(f"Ack received for {len(acked)} records")

    def _wait_connected(self) -> bool:
        """Block until CONNACK. connect_async returns before the broker has replied."""
        deadline = time.time() + CONNECT_TIMEOUT

        while time.time() < deadline:
            if self.client.is_connected():
                return True
            time.sleep(0.2)

        logging.error("Failed to connect to MQTT Broker")
        return False

    def wait_for_ack(self, times: List[str], timeout: int) -> Set[str]:
        """
        Wait until the Lambda confirms these timestamps reached the database.

        Returns the confirmed subset, which may be partial or empty on timeout -
        the caller keeps everything else buffered.
        """
        wanted = set(times)

        if not wanted:
            return set()

        deadline = time.time() + timeout

        while True:
            # Clear before checking so an ack arriving mid-check is not missed.
            self._ack_event.clear()

            with self._acked_lock:
                confirmed = wanted & self._acked

            if confirmed == wanted:
                break

            remaining = deadline - time.time()
            if remaining <= 0:
                break

            self._ack_event.wait(remaining)

        with self._acked_lock:
            confirmed = wanted & self._acked
            self._acked -= confirmed

        return confirmed

    def send_data(self, data: list) -> bool:
        """
        Publish one batch at QoS 1 and wait for the broker's PUBACK.

        True means AWS IoT Core accepted the message, not that it reached the
        database - only an ack from the Lambda proves that.
        """
        if not self.client.is_connected():
            logging.info("MQTT client not connected, attempting to reconnect...")
            try:
                self.client.reconnect()
            except Exception as e:
                logging.error(f"Error reconnecting to MQTT: {str(e)}")
                return False

            if not self._wait_connected():
                return False

            logging.info("Connected to MQTT Broker")

        message = {
            "device": self.deviceID,
            "data": data
        }

        message_json = json.dumps(message)
        logging.info(f"MQTT Data: {message_json}")

        try:
            info = self.client.publish(MQTT_TOPIC, message_json, qos=1)
            info.wait_for_publish(PUBLISH_TIMEOUT)
        except Exception as e:
            logging.error(f"Publish failed: {e}")
            return False

        if not info.is_published():
            logging.error("Broker did not acknowledge publish")
            return False

        return True
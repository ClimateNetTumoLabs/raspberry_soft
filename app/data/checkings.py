import os
import ssl
import json
import socket
import paho.mqtt.client as mqtt
from datetime import datetime
from logger_config import logging
from config import MQTT_BROKER_ENDPOINT, MQTT_TOPIC, DEVICE_ID, LOCAL_DB

import board
import adafruit_ds3231
import time as pytime

LOCAL_DB = os.path.join(LOCAL_DB, "local_data.json")


class EdgeDataManager:
    """
    Handles data publishing with MQTT, local backup when offline,
    RTC validation using DS3231, and resend mechanism.
    """

    def __init__(self):
        self.device_id = DEVICE_ID
        self.client = mqtt.Client(client_id=f"device{self.device_id}")
        self._setup_mqtt()
        self._connect_mqtt()

        # Initialize DS3231 RTC
        try:
            self.i2c = board.I2C()
            self.rtc = adafruit_ds3231.DS3231(self.i2c)
            logging.info("DS3231 RTC initialized successfully.")
        except Exception as e:
            self.rtc = None
            logging.error(f"Failed to initialize RTC: {e}")

    # ---------------- MQTT Setup ---------------- #
    def _setup_mqtt(self):
        """Configure MQTT with TLS certificates."""
        cert_dir = os.path.join(os.path.dirname(__file__), "certificates")
        self.client.tls_set(
            ca_certs=os.path.join(cert_dir, "rootCA.pem"),
            certfile=os.path.join(cert_dir, "certificate.pem.crt"),
            keyfile=os.path.join(cert_dir, "private.pem.key"),
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )
        self.client.tls_insecure_set(True)
        self.client.loop_start()

    def _connect_mqtt(self):
        """Try to connect asynchronously to MQTT broker."""
        try:
            self.client.connect_async(MQTT_BROKER_ENDPOINT, 8883, 60)
            logging.info("MQTT connection initiated.")
        except Exception as e:
            logging.error(f"MQTT connection failed: {e}")

    # ---------------- Network & RTC ---------------- #
    @staticmethod
    def is_internet_connected(host="8.8.8.8", port=53, timeout=3):
        """Check if the device is connected to the internet."""
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception:
            return False

    def get_rtc_time(self):
        """Return current RTC time, fallback to system UTC if RTC fails."""
        if self.rtc is None:
            return datetime.utcnow()
        try:
            rtc_time = pytime.mktime(self.rtc.datetime)
            return datetime.fromtimestamp(rtc_time)
        except Exception as e:
            logging.warning(f"Failed to read RTC: {e}")
            return datetime.utcnow()

    def is_rtc_ok(self):
        """Check if RTC is valid (year >= 2023)."""
        now = self.get_rtc_time()
        if now.year < 2023:
            logging.warning("RTC not synced, waiting for NTP or manual sync.")
            return False
        return True

    # ---------------- Local Save ---------------- #
    def save_locally(self, data):
        """Save unsent data to local backup file."""
        os.makedirs(os.path.dirname(LOCAL_DB), exist_ok=True)
        all_data = []
        if os.path.exists(LOCAL_DB):
            with open(LOCAL_DB, "r") as f:
                try:
                    all_data = json.load(f)
                except json.JSONDecodeError:
                    all_data = []
        all_data.append(data)
        with open(LOCAL_DB, "w") as f:
            json.dump(all_data, f)
        logging.info("Data saved locally (offline mode).")

    def resend_local_data(self):
        """Try to resend locally saved data when internet returns."""
        if not os.path.exists(LOCAL_DB):
            return

        with open(LOCAL_DB, "r") as f:
            try:
                data_list = json.load(f)
            except json.JSONDecodeError:
                data_list = []

        if not data_list:
            return

        if self.is_internet_connected():
            logging.info("Internet available, resending stored data...")
            for entry in data_list:
                try:
                    self.publish(entry, retry=False)
                except Exception as e:
                    logging.error(f"Failed to resend data: {e}")
                    break
            else:
                os.remove(LOCAL_DB)
                logging.info("All local data sent successfully.")
        else:
            logging.debug("Still offline, cannot resend local data yet.")

    # ---------------- Publishing ---------------- #
    def publish(self, payload, retry=True):
        """Send data via MQTT or save locally if offline."""
        if not self.is_rtc_ok():
            logging.warning("RTC invalid, skipping data publish.")
            return

        # payload already contains 'data': [{...}]
        data = {
            "device": f"device{self.device_id}",
            "data": payload.get("data", [])
        }

        if self.is_internet_connected():
            try:
                self.client.publish(MQTT_TOPIC, json.dumps(data))
                logging.info(f"Published to MQTT: {data}")
            except Exception as e:
                logging.error(f"MQTT publish failed: {e}")
                if retry:
                    self.save_locally(data)
        else:
            self.save_locally(data)

import json
import time
from dotenv import load_dotenv
import os
import ssl
import paho.mqtt.client as mqtt
from datetime import datetime

load_dotenv()


class MQTTPublisher:
    def __init__(self, config_manager):
        self.config = config_manager.config
        self.device_id = f"device{os.getenv('DEVICE_ID')}"
        self.broker = os.getenv("MQTT_BROKER_ENDPOINT")
        self.topic = os.getenv("MQTT_TOPIC")

        # Certificate paths (PEM files)
        self.root_ca = os.path.join(os.path.dirname(__file__), 'certificates/rootCA.pem')
        self.cert = os.path.join(os.path.dirname(__file__), "certificates/certificate.pem.crt")
        self.key = os.path.join(os.path.dirname(__file__), "certificates/private.pem.key")

        self.transmission_interval = self.config.get("transmission_interval_minutes", 15) * 60

        # MQTT client setup
        self.client = mqtt.Client(client_id=self.device_id)
        self.client.tls_set(
            ca_certs=self.root_ca,
            certfile=self.cert,
            keyfile=self.key,
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )
        self.client.tls_insecure_set(False)

        # AWS IoT uses port 8883
        print(f"[MQTT] Connecting securely to {self.broker}:8883 ...")
        self.client.connect(self.broker, 8883, 60)
        print(f"[MQTT] Connected successfully")

    def publish(self, sensors):
        """Publish merged sensor data to MQTT topic."""
        merged_data = {}
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        for name, sensor in sensors.items():
            if not sensor.enabled:
                continue

            avg = sensor.get_average(time.time())
            if not avg:
                continue

            # Map sensor-specific keys to your desired payload keys
            if name == "uv_ltr390":
                merged_data["uv"] = round(avg.get("uv_index", 0), 2)
                merged_data["lux"] = round(avg.get("light_intensity", 0), 2)
            elif name == "thp_bme280":
                merged_data["temperature"] = round(avg.get("temperature", 0), 2)
                merged_data["humidity"] = round(avg.get("humidity", 0), 2)
                merged_data["pressure"] = round(avg.get("pressure", 0), 2)
            elif name == "air_pollution_sps30":
                merged_data["pm1"] = round(avg.get("pm1", 0), 2)
                merged_data["pm2_5"] = round(avg.get("pm2_5", 0), 2)
                merged_data["pm10"] = round(avg.get("pm10", 0), 2)
            elif name == "wind_sensor":
                merged_data["speed"] = round(avg.get("wind_speed", 0), 2)
                # Convert numeric direction to cardinal
                dir_deg = avg.get("wind_direction", 0)
                merged_data["direction"] = degrees_to_cardinal(dir_deg)
            elif name == "rain_sensor":
                merged_data["rain"] = round(avg.get("rainfall", 0), 2)

        if merged_data:
            # Add timestamp
            merged_data["time"] = now

            payload = {
                "device": self.device_id,
                "data": [merged_data]
            }

            try:
                self.client.publish(self.topic, json.dumps(payload), qos=1)
                print(f"[MQTT] Published to {self.topic}: {payload}")
            except Exception as e:
                print(f"[MQTT ERROR] {e}")

    def degrees_to_cardinal(deg):
        dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        ix = int((deg + 22.5) // 45) % 8
        return dirs[ix]

    def run(self, sensors):
        """
        Main loop: sample sensors at their intervals, publish merged data every transmission_interval.
        """
        last_publish = 0
        print(f"[MQTT] Starting publish loop (interval = {self.transmission_interval // 60} min)")

        while True:
            now = time.time()

            # 1️⃣ Measure each sensor if its sampling interval passed
            for sensor in sensors.values():
                if sensor.enabled:
                    try:
                        sensor.measure(now)
                    except Exception as e:
                        print(f"[SENSOR ERROR] {sensor.name}: {e}")

            # 2️⃣ Publish merged data every transmission_interval
            if now - last_publish >= self.transmission_interval:
                merged_data = {}
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                for name, sensor in sensors.items():
                    if not sensor.enabled:
                        continue

                    avg = sensor.get_average(now)
                    if not avg:
                        continue

                    if name == "uv_ltr390":
                        merged_data["uv"] = round(avg.get("uv_index", 0))
                        merged_data["lux"] = round(avg.get("light_intensity", 0))
                    elif name == "thp_bme280":
                        merged_data["temperature"] = round(avg.get("temperature", 0), 2)
                        merged_data["humidity"] = round(avg.get("humidity", 0), 2)
                        merged_data["pressure"] = round(avg.get("pressure", 0), 2)
                    elif name == "air_pollution_sps30":
                        merged_data["pm1"] = round(avg.get("pm1", 0), 2)
                        merged_data["pm2_5"] = round(avg.get("pm2_5", 0), 2)
                        merged_data["pm10"] = round(avg.get("pm10", 0), 2)
                    elif name == "wind_sensor":
                        merged_data["speed"] = round(avg.get("wind_speed", 0), 2)
                    elif name == "rain_sensor":
                        merged_data["rain"] = round(avg.get("rainfall", 0), 2)

                if merged_data:
                    merged_data["time"] = timestamp
                    payload = {
                        "device": self.device_id,
                        "data": [merged_data]
                    }

                    try:
                        self.client.publish(self.topic, json.dumps(payload), qos=1)
                        print(f"[MQTT] Published to {self.topic}: {payload}")
                    except Exception as e:
                        print(f"[MQTT ERROR] {e}")

                last_publish = now

            # 3️⃣ Short sleep to avoid CPU overload
            time.sleep(1)

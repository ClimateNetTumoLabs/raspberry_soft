"""
BME280 and SHT45 read side by side and written straight to a PostgreSQL table,
for comparing the two sensors. Separate from the MQTT payload, which is unchanged.

Off unless COMPARE_DB_HOST is set in .env. Lives outside sensors/ so it is not
part of the metrological checksum.
"""

from config import COMPARE_DB, COMPARE_DB_TABLE, DEVICE_ID
from logger_config import logging
from sensors.bme280 import BME280Sensor
from sensors.sht45 import SHT45Sensor


class SensorComparison:
    def __init__(self):
        self.bme280 = BME280Sensor()
        self.sht45 = SHT45Sensor()
        # Both run here, whichever one config.py picks for the main payload.
        for sensor in (self.bme280, self.sht45):
            if not sensor.working:
                sensor.working = True
                sensor.setup_sensor()

    def send(self, timestamp):
        """
        One reading from each sensor at the same moment, inserted as one row.
        ponytail: the row is dropped, not buffered, when the database can't be
        reached; add buffering like DataStorage if gaps matter.
        """
        bme = self.bme280.read_data()
        sht = self.sht45.read_data()

        try:
            # Imported here so a station without psycopg2 still runs with this off.
            import psycopg2

            conn = psycopg2.connect(**COMPARE_DB, connect_timeout=5)
            try:
                with conn, conn.cursor() as cur:
                    # Table name comes from the station's own .env, same trust as the password.
                    cur.execute(
                        f"INSERT INTO {COMPARE_DB_TABLE} (device_id, time, "
                        "bme280_temperature, bme280_humidity, bme280_pressure, "
                        "sht45_temperature, sht45_humidity) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (DEVICE_ID, timestamp,
                         bme["temperature"], bme["humidity"], bme["pressure"],
                         sht["temperature"], sht["humidity"]),
                    )
            finally:
                conn.close()
            logging.info(f"[Compare] BME280 {bme}, SHT45 {sht} sent to {COMPARE_DB_TABLE}")
        except Exception as e:
            logging.error(f"[Compare] Insert into {COMPARE_DB_TABLE} failed, row dropped: {e}")

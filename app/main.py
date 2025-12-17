import time
import datetime
from config import TRANSMISSION_INTERVAL, MEASURING_TIME
from logger_config import logging
from utils.rtc import RTCControl
from utils.network import check_internet, reconnect
from utils.mqtt import MQTTClient, DEVICE_ID
from utils.data_storage import DataStorage
from utils.scheduler import calculate_next_transmission, calculate_measurement_start
from utils.sensor_manager import SensorManager
import warnings


def main():
    """Main execution loop"""
    logging.info("=== Starting ClimateNet Station ===")

    # Initialize RTC
    try:
        rtc = RTCControl()

        if check_internet():
            if not rtc.sync_from_ntp():
                logging.warning("NTP sync failed, using RTC")
                rtc.sync_system_from_rtc()
        else:
            logging.warning("No internet, using RTC time")
            rtc.sync_system_from_rtc()

        current_time = rtc.get_time()

    except Exception as e:
        logging.error(f"RTC init failed: {e}")
        current_time = datetime.datetime.now()

    # Initialize sensors
    sensor_manager = SensorManager()
    data_storage = DataStorage()

    # Initialize MQTT client
    mqtt_client = None
    if check_internet():
        try:
            mqtt_client = MQTTClient(DEVICE_ID)
            logging.info("MQTT connected")
        except Exception as e:
            logging.error(f"MQTT connection failed: {e}")
    elif reconnect():
        logging.info("Internet connected")
    else:
        logging.info("No internet connection, will save data locally")

    # Main loop
    mqtt_working = False

    while True:
        try:
            next_transmission = calculate_next_transmission(TRANSMISSION_INTERVAL)
            measurement_start = calculate_measurement_start(next_transmission, MEASURING_TIME)

            if measurement_start >= next_transmission:
                logging.warning(f"Skipping cycle, next: {next_transmission.strftime('%Y-%m-%d %H:%M:%S')}")
                while datetime.datetime.now() < next_transmission:
                    time.sleep(1)
                continue

            logging.info(f"Next transmission: {next_transmission.strftime('%Y-%m-%d %H:%M:%S')}")

            # Wait until measurement start time
            last_stored_data_attempt = 0
            while datetime.datetime.now() < measurement_start:
                if check_internet() and mqtt_client and mqtt_working and time.time() - last_stored_data_attempt > 60:
                    sent_count = data_storage.send_stored_data(mqtt_client)
                    if sent_count > 0:
                        logging.info(f"✓ Sent {sent_count} stored records")
                    last_stored_data_attempt = time.time()
                time.sleep(1)

            # Start measurements
            logging.info("+" * 15 + " Starting measurement period...")
            sensor_manager.start_measurement_period(measurement_start, next_transmission)

            # Wait until transmission time
            while datetime.datetime.now() < next_transmission:
                time.sleep(0.1)

            # Prepare and send data
            data_packet = sensor_manager.get_averaged_data(next_transmission)

            if check_internet():
                if mqtt_client is None:
                    mqtt_client = MQTTClient(DEVICE_ID)

                stored_count = data_storage.send_stored_data(mqtt_client)
                if stored_count > 0:
                    logging.info(f"✓ Sent {stored_count} stored records")

                success = False
                for attempt in range(3):
                    success = mqtt_client.send_data([data_packet])
                    if success:
                        logging.info("✓ Data sent successfully")
                        mqtt_working = True  # Mark MQTT as working
                        break
                    elif attempt < 2:
                        time.sleep(1)

                if not success:
                    logging.warning("✗ MQTT failed, saving locally")
                    mqtt_working = False
                    data_storage.save_locally(data_packet)
                    logging.info(data_packet)
            else:
                if reconnect():
                    if mqtt_client is None:
                        mqtt_client = MQTTClient(DEVICE_ID)

                    stored_count = data_storage.send_stored_data(mqtt_client)
                    if stored_count > 0:
                        logging.info(f"✓ Sent {stored_count} stored records")

                    success = False
                    for attempt in range(3):
                        success = mqtt_client.send_data([data_packet])
                        if success:
                            logging.info("✓ Data sent after reconnect")
                            mqtt_working = True
                            break
                        elif attempt < 2:
                            time.sleep(1)

                    if not success:
                        logging.warning("✗ Still no connection, saving locally")
                        mqtt_working = False
                        data_storage.save_locally(data_packet)
                        logging.info(data_packet)
                else:
                    logging.warning("✗ No internet, saving locally")
                    mqtt_working = False
                    data_storage.save_locally(data_packet)
                    logging.info(data_packet)
                    mqtt_client = None

        except KeyboardInterrupt:
            sensor_manager.cleanup()
            break
        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)

if __name__ == "__main__":
    main()

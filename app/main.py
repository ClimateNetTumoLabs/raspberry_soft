import time
import datetime
from config import TRANSMISSION_INTERVAL, MEASURING_TIME
from logger_config import logging
from utils.rtc import RTCControl
from utils.network import check_internet
from utils.mqtt import MQTTClient, DEVICE_ID
from utils.data_storage import DataStorage
from utils.scheduler import calculate_next_transmission, calculate_measurement_start
from utils.sensor_manager import SensorManager
import warnings
warnings.filterwarnings("ignore", message="Falling back from lgpio", module="gpiozero.devices")


def main():
    """Main execution loop"""
    logging.info("=== Starting ClimateNet Station ===")

    # Initialize RTC
    try:
        rtc = RTCControl()
        current_time = rtc.get_time()
        logging.info(f"RTC Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logging.error(f"RTC initialization failed: {e}")
        current_time = datetime.datetime.now()
        logging.info(f"Using system time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize sensors
    logging.info("Initializing sensors...")
    sensor_manager = SensorManager()

    # Initialize data storage
    data_storage = DataStorage()

    # Initialize MQTT client
    mqtt_client = None
    if check_internet():
        logging.info("Internet connected, initializing MQTT...")
        mqtt_client = MQTTClient(DEVICE_ID)
    else:
        logging.info("No internet connection, will save data locally")

    # Main loop
    while True:
        try:
            # Calculate next transmission time
            next_transmission = calculate_next_transmission(TRANSMISSION_INTERVAL)
            measurement_start = calculate_measurement_start(next_transmission, MEASURING_TIME)

            # Check if we need to skip this cycle (measurement start is in the past)
            if measurement_start >= next_transmission:
                logging.warning(
                    f"Skipping cycle - measurement window already passed. Next cycle: {next_transmission.strftime('%Y-%m-%d %H:%M:%S')}")

                # Wait until just after this transmission time, then recalculate
                while datetime.datetime.now() < next_transmission:
                    time.sleep(1)
                continue

            logging.info(f"Next transmission: {next_transmission.strftime('%Y-%m-%d %H:%M:%S')}")
            logging.info(f"Measurements start: {measurement_start.strftime('%Y-%m-%d %H:%M:%S')}")

            # Wait until measurement start time
            while datetime.datetime.now() < measurement_start:
                # Try to send stored data while waiting
                if check_internet() and mqtt_client:
                    sent_count = data_storage.send_stored_data(mqtt_client)
                    if sent_count > 0:
                        logging.info(f"Sent {sent_count} stored records")

            # Start measurements
            logging.info("+" * 15 + " Starting measurement period...")
            sensor_manager.start_measurement_period(measurement_start, next_transmission)

            # Wait until transmission time
            while datetime.datetime.now() < next_transmission:
                time.sleep(0.1)

            # Prepare data packet
            logging.info("Preparing data packet...")
            data_packet = sensor_manager.get_averaged_data(next_transmission)

            # Check internet and send or store
            if check_internet():
                if mqtt_client is None:
                    mqtt_client = MQTTClient(DEVICE_ID)

                success = mqtt_client.send_data([data_packet])
                if success:
                    logging.info("✓ Data sent successfully")
                    data_storage.send_stored_data(mqtt_client)
                else:
                    logging.warning("✗ MQTT send failed, saving locally")
                    data_storage.save_locally(data_packet)
            else:
                logging.warning("✗ No internet, saving locally")
                data_storage.save_locally(data_packet)
                mqtt_client = None

        except KeyboardInterrupt:
            logging.info("System stopped by user")
            sensor_manager.cleanup()
            break
        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)


if __name__ == "__main__":
    main()
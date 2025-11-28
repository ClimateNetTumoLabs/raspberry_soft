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
warnings.filterwarnings("ignore", message="Falling back from lgpio", module="gpiozero.devices")


def main():
    """Main execution loop"""
    logging.info("=== Starting ClimateNet Station ===")

    # Initialize RTC
    try:
        rtc = RTCControl()
        current_time = rtc.get_time()
        system_time = datetime.datetime.now()

        # Check if RTC time is reasonable (within 1 hour of system time)
        time_diff = abs((system_time - current_time).total_seconds())
        if time_diff > 3600:  # More than 1 hour difference
            logging.warning(f"RTC time differs from system by {time_diff} seconds. Syncing...")
            rtc.sync_from_system()
            current_time = rtc.get_time()

        logging.info(f"RTC Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"System Time: {system_time.strftime('%Y-%m-%d %H:%M:%S')}")

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
        try:
            mqtt_client = MQTTClient(DEVICE_ID)
        except Exception as e:
            logging.error(f"Couldn't connect to MQTT, {e}")
    elif reconnect():
        logging.info("Internet connected")
    else:
        logging.info("No internet connection, will save data locally")

    # Main loop
    mqtt_working = False  # Track if MQTT is currently working

    while True:
        try:
            # Calculate next transmission time
            next_transmission = calculate_next_transmission(TRANSMISSION_INTERVAL)
            measurement_start = calculate_measurement_start(next_transmission, MEASURING_TIME)

            # Check if we need to sxkip this cycle (measurement start is in the past)
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
            last_stored_data_attempt = 0
            while datetime.datetime.now() < measurement_start:
                # Only try to send stored data if we believe MQTT is working
                if check_internet() and mqtt_client and mqtt_working and time.time() - last_stored_data_attempt > 60:
                    sent_count = data_storage.send_stored_data(mqtt_client)
                    if sent_count > 0:
                        logging.info(f"Sent {sent_count} stored records")
                    last_stored_data_attempt = time.time()

                time.sleep(1)  # Small sleep to prevent busy waiting

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
            # Check internet and send or store
            if check_internet():
                # Internet is available - try to send data
                if mqtt_client is None:
                    mqtt_client = MQTTClient(DEVICE_ID)

                # Try to send data with 3 connection attempts
                success = False
                for attempt in range(3):
                    success = mqtt_client.send_data([data_packet])
                    if success:
                        logging.info("✓ Data sent successfully")
                        mqtt_working = True  # Mark MQTT as working
                        # Try to send stored data after successful connection
                        data_storage.send_stored_data(mqtt_client)
                        break
                    else:
                        logging.warning(f"✗ MQTT send attempt {attempt + 1}/3 failed")
                        if attempt < 2:  # Don't sleep after the last attempt
                            time.sleep(1)  # Wait 1 second before retry

                if not success:
                    logging.warning("✗ MQTT send failed after 3 attempts, saving locally")
                    mqtt_working = False  # Mark MQTT as not working
                    data_storage.save_locally(data_packet)
            else:
                # Internet is not available - try to reconnect
                if reconnect():
                    # Retry sending after successful reconnection
                    if mqtt_client is None:
                        mqtt_client = MQTTClient(DEVICE_ID)

                    success = False
                    for attempt in range(3):
                        success = mqtt_client.send_data([data_packet])
                        if success:
                            logging.info("✓ Data sent successfully after reconnection")
                            mqtt_working = True
                            data_storage.send_stored_data(mqtt_client)
                            break
                        else:
                            logging.warning(f"✗ MQTT send attempt {attempt + 1}/3 failed after reconnection")
                            if attempt < 2:
                                time.sleep(1)

                    if not success:
                        logging.warning("✗ Still cannot send after reconnection, saving locally")
                        mqtt_working = False
                        data_storage.save_locally(data_packet)
                else:
                    # Reconnection failed, save locally
                    logging.warning("✗ No internet and reconnection failed, saving locally")
                    mqtt_working = False
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

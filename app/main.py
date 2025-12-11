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

        # Try to sync with NTP if internet is available
        if check_internet():
            logging.info("Internet available, attempting NTP sync...")
            if rtc.sync_from_ntp():
                logging.info("Successfully synced with NTP")
            else:
                logging.warning("Failed to sync with NTP, using available time sources")

        # Get current time using the priority system
        current_time = rtc.get_time()
        system_time = datetime.datetime.now()
        rtc_time = rtc.get_rtc_time()

        # Log all time sources for debugging
        logging.info(f"RTC Hardware Time: {rtc_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"System Time: {system_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"Selected Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Check if significant time difference exists
        time_diff_system_rtc = abs((system_time - rtc_time).total_seconds())
        if time_diff_system_rtc > 60:  # More than 1 minute difference
            logging.warning(f"System and RTC differ by {time_diff_system_rtc} seconds")

            # If internet is available, sync RTC with system time
            if check_internet():
                logging.info("Syncing RTC with system time...")
                rtc.sync_from_system()

    except Exception as e:
        logging.error(f"RTC initialization failed: {e}")
        current_time = datetime.datetime.now()
        logging.info(f"Using fallback system time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

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
                    logging.info(data_packet)
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
                        logging.info(data_packet)
                else:
                    # Reconnection failed, save locally
                    logging.warning("✗ No internet and reconnection failed, saving locally")
                    mqtt_working = False
                    data_storage.save_locally(data_packet)
                    logging.info(data_packet)
                    mqtt_client = None

        except KeyboardInterrupt:
            logging.info("System stopped by user")
            sensor_manager.cleanup()
            break
        except Exception as e:
            logging.error(f"Error in main loop: {e}", exc_info=True)

if __name__ == "__main__":
    main()

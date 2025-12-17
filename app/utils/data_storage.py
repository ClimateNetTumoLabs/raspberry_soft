import json
from pathlib import Path
from typing import Dict, List

from config import LOCAL_DB
from logger_config import logging


class DataStorage:
    """Handles local storage and retrieval of sensor data"""

    # Define the exact order for measurements
    MEASUREMENT_ORDER = [
        "time",
        "uv",
        "lux",
        "temperature",
        "pressure",
        "humidity",
        "pm1",
        "pm2_5",
        "pm10",
        "speed",
        "rain",
        "direction"
    ]

    def __init__(self):
        self.local_db_path = Path(LOCAL_DB) if LOCAL_DB else Path("local_data.json")
        self.local_db_path.parent.mkdir(parents=True, exist_ok=True)

    def _order_data(self, data: Dict) -> Dict:
        """Ensure data is in the correct order and includes all fields"""
        ordered_data = {}

        for key in self.MEASUREMENT_ORDER:
            # Include the key even if it's missing, null, or 0
            ordered_data[key] = data.get(key, None)

        # Add any extra keys that weren't in the predefined order
        for key, value in data.items():
            if key not in ordered_data:
                ordered_data[key] = value

        return ordered_data

    def save_locally(self, data: Dict):
        """Save data to local JSON file in specific order"""
        try:
            # Load existing data
            if self.local_db_path.exists():
                with open(self.local_db_path, 'r') as f:
                    local_data = json.load(f)
            else:
                local_data = []

            # Order the data before appending
            ordered_data = self._order_data(data)
            local_data.append(ordered_data)

            # Save back to file
            with open(self.local_db_path, 'w') as f:
                json.dump(local_data, f, indent=2)

            logging.info(f"Data saved locally ({len(local_data)} total records)")
        except Exception as e:
            logging.error(f"Error saving data locally: {e}")

    def load_stored_data(self) -> List[Dict]:
        """Load all stored data from local file"""
        if not self.local_db_path.exists():
            return []

        try:
            with open(self.local_db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading stored data: {e}")
            return []

    def clear_stored_data(self):
        """Delete local storage file after successful send"""
        try:
            if self.local_db_path.exists():
                self.local_db_path.unlink()
                logging.info("Local storage cleared")
        except Exception as e:
            logging.error(f"Error clearing stored data: {e}")

    def send_stored_data(self, mqtt_client) -> int:
        """Send all stored data via MQTT and clear on success"""
        stored_data = self.load_stored_data()

        if not stored_data:
            return 0

        try:
            success = mqtt_client.send_data(stored_data)
            if success:
                self.clear_stored_data()
                return len(stored_data)
            else:
                logging.warning("✗ Failed to send stored data")
                return 0
        except Exception as e:
            logging.error(f"Error sending stored data: {e}")
            return 0
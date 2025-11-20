import json
from pathlib import Path
from typing import Dict, List

from config import LOCAL_DB
from logger_config import logging


class DataStorage:
    """Handles local storage and retrieval of sensor data"""

    def __init__(self):
        self.local_db_path = Path(LOCAL_DB) if LOCAL_DB else Path("local_data.json")
        self.local_db_path.parent.mkdir(parents=True, exist_ok=True)

    def save_locally(self, data: Dict):
        """Save data to local JSON file"""
        try:
            # Load existing data
            if self.local_db_path.exists():
                with open(self.local_db_path, 'r') as f:
                    local_data = json.load(f)
            else:
                local_data = []

            # Append new data
            local_data.append(data)

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
                logging.info(f"✓ Sent {len(stored_data)} stored records")
                return len(stored_data)
            else:
                logging.warning("✗ Failed to send stored data")
                return 0
        except Exception as e:
            logging.error(f"Error sending stored data: {e}")
            return 0
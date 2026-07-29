import json
import os
import time
from pathlib import Path
from typing import Dict, Iterator, List, Set

from config import LOCAL_DB, ACK_TIMEOUT, SEND_CHUNK_SIZE
from logger_config import logging

# AWS IoT Core rejects any publish larger than 128 KB. Budget the records below
# that and leave the remainder for the {"device": ..., "data": [...]} envelope.
# Not in config.py: this is a protocol limit, not something to tune per station.
MAX_PAYLOAD_BYTES = 120 * 1024


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

    def _write_all(self, records: List[Dict]):
        """
        Replace the buffer file atomically. A crash mid-write leaves the previous
        file intact instead of truncating every buffered record.
        """
        tmp_path = Path(f"{self.local_db_path}.tmp")

        with open(tmp_path, 'w') as f:
            json.dump(records, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, self.local_db_path)

    def save_locally(self, data: Dict):
        """Append data to the local buffer in specific order"""
        try:
            local_data = self.load_stored_data()

            # Order the data before appending
            local_data.append(self._order_data(data))
            self._write_all(local_data)

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
        except ValueError as e:
            # Unreadable JSON. Never return [] and let the caller overwrite it -
            # that would silently discard every buffered record.
            quarantine = Path(f"{self.local_db_path}.corrupt.{int(time.time())}")
            os.replace(self.local_db_path, quarantine)
            logging.error(f"Local buffer unreadable ({e}), moved to {quarantine}")
            return []

    def prune_acked(self, acked_times: Set[str]) -> int:
        """
        Delete only the records the Lambda confirmed are committed in the database.

        This is the single place records leave the buffer. Anything unconfirmed
        survives and is re-sent on the next cycle.
        """
        if not acked_times:
            return 0

        try:
            records = self.load_stored_data()
            remaining = [r for r in records if r.get("time") not in acked_times]
            removed = len(records) - len(remaining)

            if removed:
                self._write_all(remaining)
                logging.info(f"Removed {removed} confirmed records ({len(remaining)} still pending)")

            return removed
        except Exception as e:
            logging.error(f"Error pruning confirmed records: {e}")
            return 0

    def chunks(self, size: int = SEND_CHUNK_SIZE,
               max_bytes: int = MAX_PAYLOAD_BYTES) -> Iterator[List[Dict]]:
        """
        Yield buffered records in batches bounded by both record count and
        serialised size.

        The byte bound is the one that matters: a count alone silently stops
        working the day a record gains more fields, and every publish would then
        be rejected for exceeding the broker's limit.
        """
        records = self.load_stored_data()
        batch = []
        batch_bytes = 0

        for record in records:
            record_bytes = len(json.dumps(record)) + 1  # +1 for the separating comma

            if batch and (len(batch) >= size or batch_bytes + record_bytes > max_bytes):
                yield batch
                batch = []
                batch_bytes = 0

            if record_bytes > max_bytes:
                # ponytail: a single record this large can never be published and
                # will hold up everything behind it. Logged rather than given a
                # quarantine path, since only a schema change can cause it.
                logging.error(
                    f"Record {record.get('time')} is {record_bytes} bytes, over the "
                    f"{max_bytes} byte limit - it cannot be sent and blocks the buffer"
                )

            batch.append(record)
            batch_bytes += record_bytes

        if batch:
            yield batch

    def flush(self, mqtt_client) -> int:
        """
        Send buffered records and remove only those the Lambda confirms reached
        the database. Returns the number of confirmed records.
        """
        if mqtt_client is None:
            return 0

        confirmed_total = 0

        try:
            # chunks() iterates a snapshot taken before the first prune; later
            # batches are unaffected because pruning only removes earlier ones.
            for chunk in self.chunks():
                times = [r["time"] for r in chunk if r.get("time")]

                if not mqtt_client.send_data(chunk):
                    logging.warning("✗ Publish failed, records kept locally")
                    break

                acked = mqtt_client.wait_for_ack(times, ACK_TIMEOUT)
                confirmed_total += self.prune_acked(acked)

                if len(acked) < len(times):
                    logging.warning(
                        f"✗ Database confirmed {len(acked)}/{len(times)} records, rest kept locally"
                    )
                    break
        except Exception as e:
            logging.error(f"Error sending stored data: {e}")

        return confirmed_total
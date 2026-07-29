"""
Offline check for the local buffer and the confirm-before-delete flow.

Runs anywhere - no sensors, no broker, no .env:

    cd app && python3 test_data_storage.py
"""

import json
import logging
import shutil
import sys
import tempfile
import types
from pathlib import Path

TMP_DIR = Path(tempfile.mkdtemp())
TMP = TMP_DIR / "local_data.json"

# Stub the two flat imports data_storage needs, so this runs without
# python-dotenv and without dropping a parsing.log in the working directory.
config = types.ModuleType("config")
config.LOCAL_DB = str(TMP)
config.ACK_TIMEOUT = 1
config.SEND_CHUNK_SIZE = 100
sys.modules["config"] = config

logger_config = types.ModuleType("logger_config")
logger_config.logging = logging
sys.modules["logger_config"] = logger_config

from utils.data_storage import DataStorage, MAX_PAYLOAD_BYTES  # noqa: E402


class FakeMQTT:
    """Stands in for MQTTClient: records what was published, acks what it is told to."""

    def __init__(self, ack=None, fail=False):
        self.batches = []
        self.ack = ack if ack else (lambda times: set(times))
        self.fail = fail

    def send_data(self, data):
        self.batches.append(data)
        return not self.fail

    def wait_for_ack(self, times, timeout):
        return self.ack(times)


def record(n):
    """A full 12-field packet, sized like the ones the station really sends (~208 bytes)."""
    return {
        "time": f"2026-07-28 {n // 60:02d}:{n % 60:02d}:00",
        "uv": None, "lux": None,
        "temperature": 26.37, "pressure": 896.69, "humidity": 40.45,
        "pm1": 6.51, "pm2_5": 6.89, "pm10": 6.89,
        "speed": 12.34, "rain": 0.0, "direction": "NNW",
    }


def payload_size(batch):
    """Exactly what MQTTClient.send_data puts on the wire."""
    return len(json.dumps({"device": "device54test", "data": batch}))


def fresh():
    if TMP.exists():
        TMP.unlink()
    return DataStorage()


def test_prunes_only_confirmed_records():
    storage = fresh()
    for n in (0, 15, 30):
        storage.save_locally(record(n))

    assert len(storage.load_stored_data()) == 3

    removed = storage.prune_acked({"2026-07-28 00:00:00", "2026-07-28 00:15:00"})

    assert removed == 2
    assert [r["time"] for r in storage.load_stored_data()] == ["2026-07-28 00:30:00"]


def test_unknown_or_empty_ack_removes_nothing():
    storage = fresh()
    storage.save_locally(record(0))

    assert storage.prune_acked({"1999-01-01 00:00:00"}) == 0
    assert storage.prune_acked(set()) == 0
    assert len(storage.load_stored_data()) == 1


def test_corrupt_buffer_is_quarantined_not_overwritten():
    storage = fresh()
    storage.save_locally(record(0))
    TMP.write_text("{ truncated by a power cut")

    storage.save_locally(record(15))

    assert [r["time"] for r in storage.load_stored_data()] == ["2026-07-28 00:15:00"]

    corrupt = list(TMP_DIR.glob("local_data.json.corrupt.*"))
    assert len(corrupt) == 1
    assert corrupt[0].read_text() == "{ truncated by a power cut"
    for path in corrupt:
        path.unlink()


def test_chunks_stay_under_the_iot_core_payload_limit():
    storage = fresh()
    storage._write_all([record(n) for n in range(250)])

    assert [len(c) for c in storage.chunks(100)] == [100, 100, 50]

    for chunk in storage.chunks(100):
        assert payload_size(chunk) < 128 * 1024

    assert not Path(f"{TMP}.tmp").exists()


def test_chunks_split_by_size_when_records_outgrow_the_count():
    """
    The count bound alone is not enough: add fields to a record and 100 of them
    stop fitting in one publish, which would reject every send forever.
    """
    storage = fresh()
    fat = [dict(record(n), direction="X" * 5000) for n in range(60)]
    storage._write_all(fat)

    # 60 records is under the count bound of 100, so only the byte bound can split these.
    batches = list(storage.chunks(100))

    assert len(batches) > 1
    assert sum(len(b) for b in batches) == 60
    for batch in batches:
        assert payload_size(batch) < 128 * 1024


def test_oversized_single_record_is_reported():
    storage = fresh()
    storage._write_all([record(0), dict(record(1), direction="X" * (MAX_PAYLOAD_BYTES + 1))])

    batches = list(storage.chunks(100))

    # The impossible record is isolated in its own batch rather than poisoning a
    # good one, and both records are still accounted for - nothing is dropped.
    assert sum(len(b) for b in batches) == 2
    assert any(len(b) == 1 and payload_size(b) > MAX_PAYLOAD_BYTES for b in batches)


def test_flush_keeps_records_the_database_did_not_confirm():
    storage = fresh()
    for n in range(3):
        storage.save_locally(record(n))

    # Broker accepted the publish, but the Lambda never confirmed - the exact
    # failure the old clear-on-publish behaviour lost data on.
    assert storage.flush(FakeMQTT(ack=lambda times: set())) == 0
    assert len(storage.load_stored_data()) == 3

    # Publish itself failed.
    assert storage.flush(FakeMQTT(fail=True)) == 0
    assert len(storage.load_stored_data()) == 3

    # Partial confirmation: only the confirmed record leaves.
    assert storage.flush(FakeMQTT(ack=lambda times: {times[0]})) == 1
    assert len(storage.load_stored_data()) == 2


def test_flush_drains_a_backlog_in_chunks():
    storage = fresh()
    storage._write_all([record(n) for n in range(250)])

    client = FakeMQTT()

    assert storage.flush(client) == 250
    assert [len(b) for b in client.batches] == [100, 100, 50]
    assert storage.load_stored_data() == []


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"ok  {name}")

    shutil.rmtree(TMP_DIR)
    print("\nAll checks passed.")

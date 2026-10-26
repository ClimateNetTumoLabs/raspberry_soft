"""
Offline check for the metrological checksum.

Runs anywhere - no sensors, no .env:

    cd app && python3 test_version.py
"""

import shutil
import tempfile
from pathlib import Path

import version

APP = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp())


def checksum_of(app_dir: Path) -> str:
    version.APP_DIR = app_dir
    return version.metro_checksum()


try:
    copy = TMP / "app"
    shutil.copytree(APP, copy, ignore=shutil.ignore_patterns("venv", "__pycache__"))
    base = checksum_of(copy)

    assert checksum_of(APP) == base, "a copy of app/ must give the same checksum"

    (copy / "sensors" / "__pycache__").mkdir(exist_ok=True)
    (copy / "sensors" / "__pycache__" / "wind.cpython-311.pyc").write_bytes(b"compiled")
    assert checksum_of(copy) == base, "__pycache__ must not change the checksum"

    config = copy / "config.py"
    config.write_text(config.read_text() + "\nMQTT_TOPIC = 'changed'\n")
    assert checksum_of(copy) == base, "config.py is not metrological"

    metro = copy / "metro_config.py"
    metro.write_text(metro.read_text().replace("WIND_SPEED_COEFFICIENT = 2.4", "WIND_SPEED_COEFFICIENT = 2.5"))
    assert checksum_of(copy) != base, "a calibration change must change the checksum"

    print(f"OK {base}")
finally:
    version.APP_DIR = APP
    shutil.rmtree(TMP)

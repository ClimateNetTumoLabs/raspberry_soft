"""
Software identity, and a fingerprint of its metrological part.

The metrological part is everything that turns a raw sensor signal into a
reported value. Its SHA-256 is logged at startup and published in the
release notes, so anyone can check a station runs the approved code.

    python3 app/version.py      # prints version, SHA-256 and the files covered
"""

import hashlib
from pathlib import Path

SOFTWARE_NAME = "ClimateNet Station"
__version__ = "1.0.0"

APP_DIR = Path(__file__).resolve().parent

# Relative to app/. A directory means every .py file under it.
METRO_FILES = [
    "sensors",
    "utils/sensor_manager.py",
    "metro_config.py",
]


def _metro_files():
    for entry in METRO_FILES:
        path = APP_DIR / entry
        if path.is_dir():
            # *.py only: Python drops .pyc files into __pycache__ on first run,
            # which would change the checksum after the first boot.
            yield from path.rglob("*.py")
        else:
            yield path


def metro_file_list():
    """Every file the checksum covers, in the order it hashes them."""
    return sorted(_metro_files(), key=lambda p: p.relative_to(APP_DIR).as_posix())


def metro_checksum() -> str:
    """SHA-256 over the path and content of every metrological file, in a fixed order."""
    sha = hashlib.sha256()

    for path in metro_file_list():
        data = path.read_bytes()
        # Path and length go in too, so a rename or moving bytes between
        # files changes the result.
        sha.update(f"{path.relative_to(APP_DIR).as_posix()}\0{len(data)}\0".encode())
        sha.update(data)

    return sha.hexdigest()


if __name__ == "__main__":
    print(f"{SOFTWARE_NAME} v{__version__}")
    print(f"SHA-256 {metro_checksum()}")

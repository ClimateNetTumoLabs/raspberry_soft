import subprocess
from logger_config import logging


def chmod_tty() -> None:
    """
    Changes the permissions of the /dev/ttyAMA0 device to 777.

    Raises:
        RuntimeError: If the command to change permissions fails.
    """
    command = 'sudo chmod 777 /dev/ttyAMA0'

    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logging.info("Successfully changed mode for /dev/ttyAMA0")
        else:
            logging.error(f"Error while changing mode for /dev/ttyAMA0: {result.stderr}")
            raise RuntimeError(f"Error while changing mode for /dev/ttyAMA0: {result.stderr}")
    except Exception as e:
        logging.error(f"Error while changing mode for /dev/ttyAMA0: {str(e)}")
        raise

import subprocess
from logger_config import *


def chmod_tty():
    """
    Changes the permissions of the /dev/ttyS0 device to allow read and write access.

    This function executes a shell command to change the permissions of the /dev/ttyS0 device to 777,
    granting read, write, and execute permissions to all users.

    Raises:
        RuntimeError: If an error occurs while changing the permissions of /dev/ttyS0.
    """
    command = 'sudo chmod 777 /dev/ttyS0'

    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logging.info(f"Successfully changed mode for /dev/ttyS0")
        else:
            logging.error(f"Error while changing mode for /dev/ttyS0: {result.stderr}")
            # If the command fails, log the error message and raise a RuntimeError
            raise RuntimeError(f"Error while changing mode for /dev/ttyS0: {result.stderr}")
    except Exception as e:
        # If an exception occurs during the execution of the command, log the error and raise a RuntimeError
        logging.error(f"Error while changing mode for /dev/ttyS0: {str(e)}")
        raise

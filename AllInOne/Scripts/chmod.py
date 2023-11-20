import subprocess
from logger_config import *


def chmod_tty():
    command = 'sudo chmod 777 /dev/ttyS0'

    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logging.info(f"Successfully changed mode for /dev/ttyS0")
        else:
            logging.error(f"Error while changing mode for /dev/ttyS0: {result.stderr}")
    except Exception as e:
        logging.error(f"Error while changing mode for /dev/ttyS0 {str(e)}")
        raise

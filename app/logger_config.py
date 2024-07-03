import logging
from logging.handlers import RotatingFileHandler

# Set up rotating file handler for logging
handler = RotatingFileHandler(
    filename='parsing.log',
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Set logging level and add handler to root logger
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

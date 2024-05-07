"""
Logging Configuration

The logging configuration is designed to record parsing activities and relevant information for future analysis
and troubleshooting.

Attributes:
    - filename (str): The name of the log file where log entries will be written.
    - level (int): The log level to filter log messages. In this configuration, it is set to INFO.
    - format (str): The format of log entries, which includes the timestamp, log level, and log message.

Example:
    To enable logging in another module, you can import and use this module as follows:

    ```python
    import logger_config  # Assuming the module name is climate_net_logging.py

    # Now, you can log messages with various log levels, e.g., INFO, WARNING, ERROR, etc.
    logging.info("This is an informational message.")
    logging.error("An error occurred during parsing.")
    ```

Note:
    To control the verbosity of log messages, you can change the 'level' attribute in this module to a different
    log level (e.g., logging.DEBUG for more detailed logs or logging.ERROR for critical errors only).

"""

import logging

logging.basicConfig(
    filename='parsing.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

"""Configures the logging setup for the entire application.

This module provides a centralized function to configure the root logger.
It sets up logging to both a rotating file and the console (stdout), ensuring
that log messages are captured and managed effectively.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from config.app_config import APP_CONFIG

def setup_logging():
    """Sets up the root logger with file and console handlers.

    This function configures the application's logging to output messages to both
    a rotating log file (`app.log` by default) and the standard output.
    The log file rotates when it reaches a certain size to prevent it from
    growing indefinitely.

    Configuration details (like log file name) are pulled from `APP_CONFIG`.
    """
    log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_file = APP_CONFIG.get("log_file", "app.log")

    # Configure rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5) # 5 MB per file, 5 backup files
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    # Configure stream handler for console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)

    # Get the root logger and add handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

"""
Logging configuration for the application.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from config.app_config import APP_CONFIG

def setup_logging():
    """
    Configures the logging for the application with log rotation.
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

"""
Main application file.
"""

import logging
from utils.logging_config import setup_logging
from utils.serial_reader import start_serial_readers

if __name__ == "__main__":
    setup_logging()
    logging.info("==================================================")
    logging.info("      Serial-Tilt-ZBX Application Started       ")
    logging.info("==================================================")
    logging.info("Starting serial port readers...")
    start_serial_readers()

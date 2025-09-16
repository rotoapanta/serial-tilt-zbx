"""
Main entry point for the Serial-Tilt-ZBX application.

This script initializes the logging configuration and starts the serial port
readers, which run indefinitely to collect, process, and send data from
sensors to a Zabbix server.
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

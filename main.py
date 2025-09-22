"""
Main entry point for the Serial Tiltmeter to Zabbix application.

This script initializes the logging configuration and starts the serial port
readers, which run indefinitely to collect, process, and send data from
sensors to a Zabbix server.
"""

import logging
import signal
import threading
from utils.logging_config import setup_logging
from utils.serial_reader import start_serial_readers
from utils.zabbix_sender import preflight_check

if __name__ == "__main__":
    setup_logging()
    logging.info("==================================================")
    logging.info("    Serial Tiltmeter to Zabbix Application Started    ")
    logging.info("==================================================")
    # Create shutdown event and register signal handlers for graceful termination
    stop_event = threading.Event()

    def handle_signal(signum, frame):
        logging.info(f"Received signal {signum}. Initiating graceful shutdown...")
        stop_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Run Zabbix preflight checks (binary/connectivity/spool)
    preflight_check()

    logging.info("Starting serial port readers...")
    start_serial_readers(stop_event)
    logging.info("Serial Tiltmeter to Zabbix Application stopped.")

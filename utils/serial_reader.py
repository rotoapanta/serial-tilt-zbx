"""
Core functionality for reading from serial ports.
"""

import logging
import serial
import threading
import time
from datetime import datetime

from config.serial_config import SERIAL_PORTS
from config.serial_config import SERIAL_PORTS
from utils.data_processor import process_data


def read_serial_port(port_config):
    """Reads data from a serial port and attempts to reconnect on failure."""
    logger = logging.getLogger(__name__)
    port_name = port_config['port']
    while True:
        try:
            with serial.Serial(
                port=port_config["port"],
                baudrate=port_config["baudrate"],
                bytesize=port_config["bytesize"],
                parity=port_config["parity"],
                stopbits=port_config["stopbits"],
                timeout=port_config["timeout"],
            ) as ser:
                logger.info(f"Successfully opened port {port_name}")
                while True:
                    raw_bytes = ser.readline()
                    if raw_bytes:
                        process_data(raw_bytes, port_name)
        except serial.SerialException as e:
            logger.error(f"Error with port {port_name}: {e}")
            logger.info(f"Retrying to connect to {port_name} in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.critical(f"An unexpected error occurred on port {port_name}: {e}")
            logger.info(f"Retrying to connect to {port_name} in 5 seconds...")
            time.sleep(5)

def start_serial_readers():
    """Starts a thread for each serial port to read data simultaneously."""
    logger = logging.getLogger(__name__)
    threads = []
    for port_config in SERIAL_PORTS:
        thread = threading.Thread(target=read_serial_port, args=(port_config,))
        thread.daemon = True  # Daemon threads will exit when the main program exits
        thread.start()
        threads.append(thread)

    try:
        # Keep the main thread alive, allowing daemon threads to run
        # and to catch KeyboardInterrupt gracefully.
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        logger.info("Stopping serial port readers...")

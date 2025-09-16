"""Handles the concurrent reading of multiple serial ports.

This module is responsible for:
- Creating and managing a separate thread for each serial port defined in the
  configuration.
- Continuously reading data from each port.
- Handling serial port errors (e.g., disconnection) and attempting to
  reconnect automatically.
- Passing the raw data read from the port to the data processor.
"""

import logging
import serial
import threading
import time

from config.serial_config import SERIAL_PORTS
from utils.data_processor import process_data


def read_serial_port(port_config):
    """Continuously reads data from a single serial port in an infinite loop.

    This function opens a serial port based on the provided configuration.
    It reads data line by line and passes it to `process_data`. If the port
    cannot be opened or an error occurs during reading, it logs the error
    and attempts to reconnect after a short delay.

    Args:
        port_config (dict): A dictionary containing the configuration for the
                            serial port (e.g., 'port', 'baudrate').
    """
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
    """Initializes and starts a daemon thread for each configured serial port.

    This function iterates through the `SERIAL_PORTS` configuration, creating a
    separate thread for each port that targets the `read_serial_port` function.
    It then keeps the main thread alive by joining the threads, allowing the
    program to run indefinitely until interrupted (e.g., with Ctrl+C).
    """
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

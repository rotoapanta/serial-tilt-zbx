"""Orchestrates the processing of raw data from serial ports.

This module acts as a central hub after data is read from a serial port.
It receives raw byte data, logs it, passes it to the parser, and then
distributes the parsed data to other utilities for storage and submission
to Zabbix.
"""

import logging
from datetime import datetime

from parsers.data_parser import parse_raw_data
from utils.data_storage import save_inclinometer_data, save_pluviometer_data
from utils.zabbix_sender import send_inclinometer_to_zabbix, send_pluviometer_to_zabbix


def process_data(raw_bytes, port_name):
    """Receives raw bytes, parses them, and sends the data for storage and monitoring.

    This is the main data processing function. It takes the raw byte string from
    the serial reader, logs the raw and hex representations, and calls the
    `parse_raw_data` function. If parsing is successful, it logs the parsed
    data and then calls functions to save the data locally and send it to Zabbix.

    Args:
        raw_bytes (bytes): The raw byte string read from the serial port.
        port_name (str): The name of the port from which the data was read (e.g., '/dev/ttyUSB0').
    """
    logger = logging.getLogger(__name__)
    hex_representation = raw_bytes.hex(' ')
    logger.debug(f"Received raw bytes from {port_name}: {raw_bytes!r}")
    logger.debug(f"Hex data from {port_name}: {hex_representation}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parsed_data = parse_raw_data(raw_bytes)
    if parsed_data:
        logger.info(f"{timestamp} - {port_name}: {parsed_data}")
        # Save the data to the respective files
        save_inclinometer_data(parsed_data)
        save_pluviometer_data(parsed_data)

        # Send the data to Zabbix
        send_inclinometer_to_zabbix(parsed_data)
        send_pluviometer_to_zabbix(parsed_data)

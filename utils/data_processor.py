"""
Data processing module.
"""

import logging
from datetime import datetime

from parsers.data_parser import parse_raw_data
from utils.data_storage import save_inclinometer_data, save_pluviometer_data
from utils.zabbix_sender import send_inclinometer_to_zabbix, send_pluviometer_to_zabbix


def process_data(raw_bytes, port_name):
    """Processes raw data from the serial port."""
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

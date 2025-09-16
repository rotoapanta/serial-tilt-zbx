"""Handles the submission of data to a Zabbix server.

This module uses the `zabbix_sender` command-line utility to send data
points to a Zabbix server. It constructs the necessary commands and handles
potential errors, such as the command not being found, timeouts, or errors
returned from the Zabbix server.
"""
import subprocess
import logging
from config.app_config import APP_CONFIG
from config.zabbix_config import ZABBIX_SERVER, ZABBIX_PORT

def _send_to_zabbix(host_name, key, value):
    """Constructs and executes a `zabbix_sender` command to send a single data point.

    This is a helper function that builds the command with the server details,
    host name, item key, and value. It executes the command as a subprocess,
    captures the output, and logs the result. It includes error handling for
    common issues like timeouts or command failures.

    Args:
        host_name (str): The name of the host in Zabbix to which the data belongs.
        key (str): The item key in Zabbix for this data point.
        value (any): The value to be sent. It will be converted to a string.
    """
    logger = logging.getLogger(__name__)
    command = [
        'zabbix_sender',
        '-z', ZABBIX_SERVER,
        '-p', str(ZABBIX_PORT),
        '-s', host_name,
        '-k', key,
        '-o', str(value)
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=10)
        logger.info(f"Successfully sent to Zabbix: {host_name} [{key}] = {value}")
        # The zabbix_sender output can be useful for debugging
        if result.stdout:
            logger.debug(f"Zabbix sender output: {result.stdout.strip()}")
    except FileNotFoundError:
        logger.error("'zabbix_sender' command not found. Make sure it is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        # Log both stdout and stderr from the failed command to get more details
        logger.error(f"Error sending to Zabbix for host '{host_name}'. Response from server:")
        if e.stdout:
            logger.error(f"  stdout: {e.stdout.strip()}")
        if e.stderr:
            logger.error(f"  stderr: {e.stderr.strip()}")
    except subprocess.TimeoutExpired:
        logger.error(f"Zabbix sender command timed out for host '{host_name}'.")

def send_inclinometer_to_zabbix(data):
    """Prepares and sends all inclinometer data points to Zabbix.

    This function extracts the inclinometer data and station name from the main
    data dictionary. It constructs a Zabbix host name by appending "_IN".
    It then iterates through the inclinometer data, looks up the corresponding
    Zabbix item key from the application config, and calls `_send_to_zabbix`
    for each data point.

    Args:
        data (dict): The dictionary of parsed data containing 'station_name'
                     and 'inclinometer' keys.
    """
    logger = logging.getLogger(__name__)
    try:
        base_station_name = data['station_name']
        incli_data = data['inclinometer']
        host_name = f"{base_station_name}_IN"

        # Get the key mapping from the config
        key_map = APP_CONFIG.get("zabbix_keys", {}).get("inclinometer", {})

        for data_key, value in incli_data.items():
            zabbix_key = key_map.get(data_key)
            if zabbix_key:
                _send_to_zabbix(host_name, zabbix_key, value)
            else:
                logger.warning(f"No Zabbix key mapping found for inclinometer data '{data_key}'.")

    except KeyError as e:
        logger.error(f"Error preparing inclinometer data for Zabbix: Missing key {e}")

def send_pluviometer_to_zabbix(data):
    """Prepares and sends all pluviometer data points to Zabbix.

    This function extracts the pluviometer data and station name from the main
    data dictionary. It constructs a Zabbix host name by appending "_PL".
    It then iterates through the pluviometer data, looks up the corresponding
    Zabbix item key from the application config, and calls `_send_to_zabbix`
    for each data point.

    Args:
        data (dict): The dictionary of parsed data containing 'station_name'
                     and 'pluviometer' keys.
    """
    logger = logging.getLogger(__name__)
    try:
        base_station_name = data['station_name']
        pluvio_data = data['pluviometer']
        host_name = f"{base_station_name}_PL"

        # Get the key mapping from the config
        key_map = APP_CONFIG.get("zabbix_keys", {}).get("pluviometer", {})

        for data_key, value in pluvio_data.items():
            zabbix_key = key_map.get(data_key)
            if zabbix_key:
                _send_to_zabbix(host_name, zabbix_key, value)
            else:
                logger.warning(f"No Zabbix key mapping found for pluviometer data '{data_key}'.")

    except KeyError as e:
        logger.error(f"Error preparing pluviometer data for Zabbix: Missing key {e}")

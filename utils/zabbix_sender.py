"""
Handles sending data to a Zabbix server using zabbix_sender.
"""
import subprocess
import logging
from config.app_config import APP_CONFIG
from config.zabbix_config import ZABBIX_SERVER, ZABBIX_PORT

def _send_to_zabbix(host_name, key, value):
    """Constructs and executes a zabbix_sender command."""
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
    """Prepares and sends inclinometer data to Zabbix dynamically."""
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
    """Prepares and sends pluviometer data to Zabbix dynamically."""
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

"""
Handles sending data to a Zabbix server using zabbix_sender.
"""
import subprocess
import logging
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
    """Prepares and sends inclinometer data to Zabbix."""
    logger = logging.getLogger(__name__)
    try:
        base_station_name = data['station_name']
        incli_data = data['inclinometer']
        
        host_name = f"{base_station_name}_IN"
        
        zabbix_keys = {
            "axis.radial": incli_data['radial'],
            "axis.tangential": incli_data['tangential'],
            "incl.temp": incli_data['temperature'],
            "incl.vbat": incli_data['voltage']
        }
        
        for key, value in zabbix_keys.items():
            _send_to_zabbix(host_name, key, value)
            
    except KeyError as e:
        logger.error(f"Error preparing inclinometer data for Zabbix: Missing key {e}")

def send_pluviometer_to_zabbix(data):
    """Prepares and sends pluviometer data to Zabbix."""
    logger = logging.getLogger(__name__)
    try:
        base_station_name = data['station_name']
        pluvio_data = data['pluviometer']
        
        host_name = f"{base_station_name}_PL"
        
        zabbix_keys = {
            "rain.level": pluvio_data['rain_level'],
            "pluvio.vbat": pluvio_data['voltage']
        }
        
        for key, value in zabbix_keys.items():
            _send_to_zabbix(host_name, key, value)

    except KeyError as e:
        logger.error(f"Error preparing pluviometer data for Zabbix: Missing key {e}")

"""
Handles sending data to a Zabbix server using zabbix_sender.
"""
import subprocess
from config.zabbix_config import ZABBIX_SERVER, ZABBIX_PORT

def _send_to_zabbix(host_name, key, value):
    """Constructs and executes a zabbix_sender command."""
    command = [
        'zabbix_sender',
        '-z', ZABBIX_SERVER,
        '-p', str(ZABBIX_PORT),
        '-s', host_name,
        '-k', key,
        '-o', str(value)
    ]
    
    try:
        # We use subprocess.run for a simple, blocking call.
        # For high-throughput, you might consider asynchronous methods.
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=10)
        print(f"Successfully sent to Zabbix: {host_name} [{key}] = {value}")
        # For debugging, you can print the output from zabbix_sender
        # print(result.stdout)
    except FileNotFoundError:
        print("Error: 'zabbix_sender' command not found. Make sure it is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error sending to Zabbix: {e.stderr}")
    except subprocess.TimeoutExpired:
        print("Error: Zabbix sender command timed out.")

def send_inclinometer_to_zabbix(data):
    """Prepares and sends inclinometer data to Zabbix."""
    try:
        base_station_name = data['station_name']
        incli_data = data['inclinometer']
        
        host_name = f"{base_station_name}_IN"
        
        # Map your data to the Zabbix keys you have configured
        zabbix_keys = {
            "axis.radial": incli_data['radial'],
            "axis.tangential": incli_data['tangential'],
            "incl.temp": incli_data['temperature'],
            "incl.vbat": incli_data['voltage']
        }
        
        for key, value in zabbix_keys.items():
            _send_to_zabbix(host_name, key, value)
            
    except KeyError as e:
        print(f"Error preparing inclinometer data for Zabbix: Missing key {e}")

def send_pluviometer_to_zabbix(data):
    """Prepares and sends pluviometer data to Zabbix."""
    try:
        base_station_name = data['station_name']
        pluvio_data = data['pluviometer']
        
        host_name = f"{base_station_name}_PL"
        
        # Map your data to the Zabbix keys you have configured
        zabbix_keys = {
            "rain.level": pluvio_data['rain_level'],
            "pluvio.vbat": pluvio_data['voltage']
        }
        
        for key, value in zabbix_keys.items():
            _send_to_zabbix(host_name, key, value)

    except KeyError as e:
        print(f"Error preparing pluviometer data for Zabbix: Missing key {e}")

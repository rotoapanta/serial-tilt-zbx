"""Handles the local storage of sensor data into TSV files.

This module is responsible for writing the parsed inclinometer and pluviometer
data into structured, daily log files in a Tab-Separated Values (TSV) format.
It automatically manages directory creation based on sensor type and station name.
"""
import os
import logging
import threading
from datetime import datetime
from config.app_config import APP_CONFIG

BASE_DIR = APP_CONFIG.get("base_dir", "./DTA")

# In-memory locks to protect per-file writes across threads
_file_locks = {}
_file_locks_lock = threading.Lock()

def _get_file_lock(path):
    with _file_locks_lock:
        lock = _file_locks.get(path)
        if lock is None:
            lock = threading.Lock()
            _file_locks[path] = lock
        return lock

def _ensure_dir_exists(path):
    """Ensures that a directory exists, creating it if necessary.

    This is a helper function that uses `os.makedirs` with `exist_ok=True`
    to prevent errors if the directory already exists.

    Args:
        path (str): The full path of the directory to create.
    """
    os.makedirs(path, exist_ok=True)

def save_inclinometer_data(data):
    """Saves inclinometer data to a daily TSV file.

    Extracts inclinometer data from the parsed data dictionary, creates a
    directory structure (`<BASE_DIR>/INCLINOMETRIA/<station_name>/`),
    and appends a new line to a file named with the current date (YYYY-M-D.tsv).
    If the file doesn't exist, it adds a multi-line header first.

    Args:
        data (dict): The dictionary of parsed data containing 'station_name',
                     'station_number', and 'inclinometer' keys.
    """
    try:
        station_name = data['station_name']
        station_number = data['station_number']
        incli_data = data['inclinometer']
        
        # Create directory
        today = datetime.now()
        dir_path = os.path.join(BASE_DIR, "INCLINOMETRIA", station_name)
        _ensure_dir_exists(dir_path)
        
        # File path
        file_path = os.path.join(dir_path, today.strftime("%Y-%-m-%-d") + ".tsv")

        # Guarded write to avoid race conditions across threads
        lock = _get_file_lock(file_path)
        with lock:
            write_header = not os.path.exists(file_path)
            with open(file_path, 'a') as f:
                if write_header:
                    f.write(f"TIPO:INCLINOMETRIA\n")
                    f.write(f"NOMBRE:{station_name}\n")
                    f.write(f"IDENTIFICADOR:{station_number}\n")
                    f.write("\n")
                    f.write("FECHA\tTIEMPO\tX RADIAL\tY TANGENCIAL\tTEMPERATURA\tBATERIA\n")
                    f.write("\t\tmicro radianes\tmicro radianes\tgrados centigrados\tvoltios\n")
                
                # Write data
                date_str = today.strftime("%d/%m/%Y")
                time_str = today.strftime("%H:%M:%S")
                f.write(f"{date_str}\t{time_str}\t{incli_data['radial']}\t{incli_data['tangential']}\t{incli_data['temperature']}\t{incli_data['voltage']}\n")
            
    except (KeyError, IOError) as e:
        logging.getLogger(__name__).error(f"Error saving inclinometer data: {e}")

def save_pluviometer_data(data):
    """Saves pluviometer data to a daily TSV file.

    Extracts pluviometer data from the parsed data dictionary, creates a
    directory structure (`<BASE_DIR>/PLUVIOMETRIA/<station_name>/`),
    and appends a new line to a file named with the current date (YYYY-M-D.tsv).
    If the file doesn't exist, it adds a multi-line header first.

    Args:
        data (dict): The dictionary of parsed data containing 'station_name',
                     'station_number', and 'pluviometer' keys.
    """
    try:
        station_name = data['station_name']
        station_number = data['station_number']
        pluvio_data = data['pluviometer']
        
        # Create directory
        today = datetime.now()
        dir_path = os.path.join(BASE_DIR, "PLUVIOMETRIA", station_name)
        _ensure_dir_exists(dir_path)
        
        # File path
        file_path = os.path.join(dir_path, today.strftime("%Y-%-m-%-d") + ".tsv")

        # Guarded write to avoid race conditions across threads
        lock = _get_file_lock(file_path)
        with lock:
            write_header = not os.path.exists(file_path)
            with open(file_path, 'a') as f:
                if write_header:
                    f.write(f"TIPO:PLUVIOMETRIA\n")
                    f.write(f"NOMBRE:{station_name}\n")
                    f.write(f"IDENTIFICADOR:{station_number}\n")
                    f.write("\n")
                    f.write("FECHA\tTIEMPO\tNIVEL\tBATERIA\n")
                    f.write("\t\tmilimetros\tvoltios\n")
                
                # Write data
                date_str = today.strftime("%d/%m/%Y")
                time_str = today.strftime("%H:%M:%S")
                f.write(f"{date_str}\t{time_str}\t{pluvio_data['rain_level']}\t{pluvio_data['voltage']}\n")

    except (KeyError, IOError) as e:
        logging.getLogger(__name__).error(f"Error saving pluviometer data: {e}")

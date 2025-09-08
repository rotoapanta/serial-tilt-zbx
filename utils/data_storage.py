"""
Handles storage of parsed data into TSV files.
"""
import os
import logging
from datetime import datetime
from config.app_config import APP_CONFIG

BASE_DIR = APP_CONFIG.get("base_dir", "./DTA")

def _ensure_dir_exists(path):
    """Creates a directory if it does not exist."""
    os.makedirs(path, exist_ok=True)

def save_inclinometer_data(data):
    """Saves inclinometer data to a TSV file."""
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
        
        # Check if file needs header
        write_header = not os.path.exists(file_path)
        
        with open(file_path, 'a') as f:
            if write_header:
                f.write(f"TIPO:INCLINOMETRIA\n")
                f.write(f"NOMBRE:{station_name}\n")
                f.write(f"IDENTIFICADOR:{station_number}\n")
                f.write("FECHA\tTIEMPO\tX RADIAL\tY TANGENCIAL\tTEMPERATURA\tBATERIA\n")
                f.write("\t\tmicro radianes\tmicro radianes\tgrados centigrados\tvoltios\n")
            
            # Write data
            date_str = today.strftime("%d/%m/%Y")
            time_str = today.strftime("%H:%M:%S")
            f.write(f"{date_str}\t{time_str}\t{incli_data['radial']}\t{incli_data['tangential']}\t{incli_data['temperature']}\t{incli_data['voltage']}\n")
            
    except (KeyError, IOError) as e:
        logging.getLogger(__name__).error(f"Error saving inclinometer data: {e}")

def save_pluviometer_data(data):
    """Saves pluviometer data to a TSV file."""
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
        
        # Check if file needs header
        write_header = not os.path.exists(file_path)
        
        with open(file_path, 'a') as f:
            if write_header:
                f.write(f"TIPO:PLUVIOMETRIA\n")
                f.write(f"NOMBRE:{station_name}\n")
                f.write(f"IDENTIFICADOR:{station_number}\n")
                f.write("FECHA\tTIEMPO\tNIVEL\tBATERIA\n")
                f.write("\t\tmilimetros\tvoltios\n")
            
            # Write data
            date_str = today.strftime("%d/%m/%Y")
            time_str = today.strftime("%H:%M:%S")
            f.write(f"{date_str}\t{time_str}\t{pluvio_data['rain_level']}\t{pluvio_data['voltage']}\n")

    except (KeyError, IOError) as e:
        logging.getLogger(__name__).error(f"Error saving pluviometer data: {e}")

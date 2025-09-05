"""
Parses raw data from the serial port.
"""
import struct

def parse_raw_data(raw_bytes):
    """
    Parses a raw byte string from the inclinometer and pluviometer.
    
    Args:
        raw_bytes (bytes): The raw byte string from the serial port.
        
    Returns:
        A dictionary with the parsed data, or None if parsing fails.
    """
    if not (raw_bytes.startswith(b'~') and raw_bytes.endswith(b'~\n')):
        return None

    # The data seems to be split by ~~, let's find the parts
    parts = raw_bytes.strip().split(b'~~~')
    if len(parts) != 2:
        # Fallback for the previous format for a bit more of compatibility
        parts = raw_bytes.strip().split(b'~~')
        if len(parts) != 2:
            return None

    try:
        inclinometer_part = parts[0]
        pluviometer_part = parts[1]

        # --- Inclinometer Data --- 
        # Header: 7e 1c 00 00 00 00 00 01 01 00 01
        # Data: 2d 30 30 34 34 2e 37 2b 30 30 39 37 2e 38 2b 30 30 30 39 2e 34 2b 30 30 31 32 2e 30
        # Footer: 00 00 7e
        inclinometer_data = inclinometer_part.strip(b'~')
        station_type = inclinometer_data[7]
        station_number = inclinometer_data[8]
        network_id = inclinometer_data[10]

        # Extract the data part and decode it
        inclinometer_values_raw = inclinometer_data[11:34].decode('utf-8')
        inclinometer_values = re.findall(r'([+-]\d+\.\d+)', inclinometer_values_raw)

        # --- Pluviometer Data ---
        # Header: 0e 00 00 00 00 00 00 01 00 01
        # Data: 2b 30 30 30 30 2e 30 2b 30 30 31 32 2e 30
        # Footer: 00 00 7e
        pluviometer_data = pluviometer_part.strip(b'~')
        pluviometer_values_raw = pluviometer_data[10:25].decode('utf-8')
        pluviometer_values = re.findall(r'([+-]\d+\.\d+)', pluviometer_values_raw)

        if len(inclinometer_values) != 4 or len(pluviometer_values) != 2:
            return None

        parsed_data = {
            "type": "TILT_RAIN",
            "station_type": station_type,
            "station_number": station_number,
            "network_id": network_id,
            "inclinometer": {
                "radial": float(inclinometer_values[0]),
                "tangential": float(inclinometer_values[1]),
                "temperature": float(inclinometer_values[2]),
                "voltage": float(inclinometer_values[3])
            },
            "pluviometer": {
                "rain_level": float(pluviometer_values[0]),
                "voltage": float(pluviometer_values[1])
            }
        }
        return parsed_data
    except (ValueError, IndexError, struct.error):
        return None

import re

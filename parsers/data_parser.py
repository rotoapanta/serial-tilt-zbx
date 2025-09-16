"""Parses proprietary data frames from the sensors.

This module is responsible for decoding the specific data format sent by the
inclinometer and pluviometer sensors. The format is a hybrid of binary and ASCII
characters, delimited by tilde (`~`) characters.
"""
import re
import logging

from config.station_mapping import STATION_NAMES

def parse_raw_data(raw_bytes):
    """Parses a raw, hybrid binary/ASCII byte string from the sensors.

    The expected data frame has a structure like `~<inclinometer_frame>~~<pluviometer_frame>~\n`.
    This function splits the frame into its two main parts, extracts binary header
    information (like station ID) from the first part, and uses regular expressions
    to find floating-point values in the ASCII parts of both frames.

    Args:
        raw_bytes (bytes): The raw byte string read from the serial port.

    Returns:
        dict: A dictionary containing the structured, parsed data if successful.
        None: If the frame is malformed, incomplete, or cannot be parsed.
    """
    try:
        # The full line is expected to be b'~...~~...~\n'
        if not raw_bytes.startswith(b'~') or b'~~' not in raw_bytes:
            return None

        # b'~A~~B~\n'.strip() -> b'~A~~B~'
        # .split(b'~~') -> [b'~A', b'B~']
        parts = raw_bytes.strip().split(b'~~')
        if len(parts) != 2:
            return None

        # --- Inclinometer Part ---
        # parts[0] is b'~A' where A is the inclinometer frame content
        inclinometer_frame = parts[0]
        if not inclinometer_frame.startswith(b'~'):
            return None

        # Get header data from the inclinometer frame (indices are 0-based from the start of the frame)
        station_type = inclinometer_frame[7]
        station_number = inclinometer_frame[8]
        network_id = inclinometer_frame[10]

        # Decode the ASCII part of the frame (from index 11 onwards) and find values
        inclinometer_ascii_part = inclinometer_frame[11:].decode('ascii', errors='ignore')
        pattern = r'([+-]\d+\.\d+)'
        inclinometer_values = re.findall(pattern, inclinometer_ascii_part)

        # --- Pluviometer Part ---
        # parts[1] is b'B~'. We reconstruct the full frame to be `~B~`
        pluviometer_frame = b'~' + parts[1]
        
        # The ASCII part starts at index 10 of the pluviometer frame
        pluviometer_ascii_part = pluviometer_frame[10:].decode('ascii', errors='ignore')
        pluviometer_values = re.findall(pattern, pluviometer_ascii_part)

        if len(inclinometer_values) != 4 or len(pluviometer_values) != 2:
            return None

        station_name = STATION_NAMES.get(station_number, f"Unknown_{station_number}")

        parsed_data = {
            "type": "TILT_RAIN",
            "station_name": station_name,
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
    except (ValueError, IndexError, TypeError) as e:
        logging.getLogger(__name__).error(f"Failed to parse raw data: {raw_bytes!r}. Error: {e}")
        return None

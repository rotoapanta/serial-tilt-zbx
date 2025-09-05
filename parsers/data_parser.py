"""
Parses raw data from the serial port.
"""
import re

def parse_raw_data(raw_data):
    """
    Parses a raw data string from the inclinometer and pluviometer.
    
    Args:
        raw_data (str): The raw data string from the serial port.
        Example: ~-0045.0+0098.2+0009.4+0012.0~~+0000.0+0012.0~
        
    Returns:
        A dictionary with the parsed data, or None if parsing fails.
    """
    if not (raw_data.startswith('~') and raw_data.endswith('~')):
        return None

    # Remove the outer '~' characters
    cleaned_data = raw_data[1:-1]
    
    # Split into inclinometer and pluviometer parts
    parts = cleaned_data.split('~~')
    if len(parts) != 2:
        return None
        
    inclinometer_raw, pluviometer_raw = parts

    # Use regex to find all the values. The format is a sign, followed by digits.
    # Example: -0045.0, +0098.2
    pattern = r'([+-]\d+\.\d+)'
    
    inclinometer_values = re.findall(pattern, inclinometer_raw)
    pluviometer_values = re.findall(pattern, pluviometer_raw)

    if len(inclinometer_values) != 4 or len(pluviometer_values) != 2:
        return None

    try:
        parsed_data = {
            "type": "TILT_RAIN",
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
    except (ValueError, IndexError):
        return None

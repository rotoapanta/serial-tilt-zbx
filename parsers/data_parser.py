
"""
Parses raw data from the serial port.
"""

def parse_raw_data(raw_data):
    """
    Parses a raw data string and extracts relevant information.
    
    Args:
        raw_data (str): The raw data string from the serial port.
        
    Returns:
        A dictionary with the parsed data, or None if parsing fails.
    """
    # Implement your data parsing logic here
    # This is just an example
    if "TILT" in raw_data:
        try:
            parts = raw_data.split(',')
            return {
                "type": "TILT",
                "x": float(parts[1]),
                "y": float(parts[2]),
            }
        except (ValueError, IndexError):
            return None
    return None

"""
Core functionality for reading from serial ports.
"""

import serial
import threading
import time
from datetime import datetime

from config.serial_config import SERIAL_PORTS
from parsers.data_parser import parse_raw_data
from utils.data_storage import save_inclinometer_data, save_pluviometer_data

def read_serial_port(port_config):
    """Reads data from a serial port, parses it, and prints the result."""
    try:
        with serial.Serial(
            port=port_config["port"],
            baudrate=port_config["baudrate"],
            bytesize=port_config["bytesize"],
            parity=port_config["parity"],
            stopbits=port_config["stopbits"],
            timeout=port_config["timeout"],
        ) as ser:
            print(f"Successfully opened port {port_config['port']}")
            while True:
                raw_bytes = ser.readline()
                if raw_bytes:
                    hex_representation = raw_bytes.hex(' ')
                    print(f"Received raw bytes from {port_config['port']}: {raw_bytes!r}")
                    print(f"Hex data from {port_config['port']}: {hex_representation}")
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    parsed_data = parse_raw_data(raw_bytes)
                    if parsed_data:
                        print(f"{timestamp} - {port_config['port']}: {parsed_data}")
                        # Save the data to the respective files
                        save_inclinometer_data(parsed_data)
                        save_pluviometer_data(parsed_data)
    except serial.SerialException as e:
        print(f"Error opening port {port_config['port']}: {e}")

def start_serial_readers():
    """Starts a thread for each serial port to read data simultaneously."""
    threads = []
    for port_config in SERIAL_PORTS:
        thread = threading.Thread(target=read_serial_port, args=(port_config,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping serial port readers...")

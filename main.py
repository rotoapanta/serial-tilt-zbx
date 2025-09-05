"""
Main application file.
"""

from utils.serial_reader import start_serial_readers

if __name__ == "__main__":
    print("Starting serial port readers...")
    start_serial_readers()

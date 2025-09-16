"""Provides the serial port configurations for the application.

This module extracts the list of serial port settings from the main
application configuration (`APP_CONFIG`) loaded from `config.json`.

The `SERIAL_PORTS` variable is a list of dictionaries, where each dictionary
defines the parameters for one serial port (e.g., port, baudrate, etc.).
"""

from config.app_config import APP_CONFIG

SERIAL_PORTS = APP_CONFIG.get("serial_ports", [])

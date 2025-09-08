"""
Serial port configuration.
"""

from config.app_config import APP_CONFIG

SERIAL_PORTS = APP_CONFIG.get("serial_ports", [])

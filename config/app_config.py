"""Loads and provides the main application configuration.

This module is responsible for loading the central `config.json` file.
It defines a global `APP_CONFIG` dictionary that can be imported by other
modules to access configuration parameters like log file paths, Zabbix key
mappings, etc.
"""

import json
import logging

def load_app_config():
    """Loads the main application configuration from the `config.json` file.

    This function attempts to open and parse `config.json`. It includes error
    handling for cases where the file is not found or contains invalid JSON,
    returning an empty dictionary in such cases to prevent crashes.

    Returns:
        dict: A dictionary containing the application configuration.
    """
    logger = logging.getLogger(__name__)
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            return config
    except FileNotFoundError:
        logger.error("The configuration file config.json was not found.")
        return {}
    except json.JSONDecodeError:
        logger.error("Error decoding the configuration file config.json.")
        return {}

APP_CONFIG = load_app_config()

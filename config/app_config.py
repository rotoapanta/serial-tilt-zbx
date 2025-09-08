"""
Application configuration loader.
"""

import json
import logging

def load_app_config():
    """Loads the application configuration from config.json."""
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

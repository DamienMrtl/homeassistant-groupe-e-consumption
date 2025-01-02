"""Constants for Groupe E Consumption integration."""
from logging import Logger, getLogger

# Base component constants
NAME = "Groupe E Consumption"
DOMAIN = "groupe_e_consumption"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
ATTRIBUTION = "Data provided by Groupe E API"
ISSUE_URL = "https://github.com/DamienMrtl/homeassistant-groupe-e-consumption/issues"

# Icons
ICON = "mdi:format-quote-close"

# Platforms
PLATFORMS = ["sensor"]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# API details
TOKEN_URL = "YOUR_TOKEN_URL"
API_URL = "YOUR_API_URL"
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
# Set up logging
_LOGGER: Logger = getLogger(__package__)
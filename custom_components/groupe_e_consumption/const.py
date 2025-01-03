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
CONF_PREMISE_ID = "premise_id"
CONF_PARTNER_ID = "partner_id"

# API details
API_URL = "YOUR_API_URL"

# OAuth2 details
TOKEN_URL = (
    "https://login.my.groupe-e.ch/realms/my-groupe-e/protocol/openid-connect/token"
)
CLIENT_ID = "portal"
CLIENT_SECRET = "7EpnoktF0wOR5gwZPxPR2w7__p_rinCT4pcHywFFve0"
SCOPE = "openid email impersonate portal"

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

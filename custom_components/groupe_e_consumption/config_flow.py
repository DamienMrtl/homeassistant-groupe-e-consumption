"""Config flow for Groupe E Consumption integration."""

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import GroupeEConsumptionAPI
from .const import (
    CONF_PARTNER_ID,
    CONF_PASSWORD,
    CONF_PREMISE_ID,
    CONF_USERNAME,
    DOMAIN,
    _LOGGER,
)


class GroupeEConsumptionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Groupe E Consumption."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                api = GroupeEConsumptionAPI(self.hass)
                token = await api.authenticate(
                    user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
                )
                if token:
                    premise_id = await api.get_premise_id(token)
                    partner_id = await api.get_partner_id(token)
                    await api.close()

                    if premise_id and partner_id:
                        user_input[CONF_PREMISE_ID] = premise_id
                        user_input[CONF_PARTNER_ID] = partner_id
                        return self.async_create_entry(
                            title="Groupe E Consumption",
                            data=user_input,
                        )
                    else:
                        errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return GroupeEConsumptionOptionsFlowHandler(config_entry)


# class GroupeEConsumptionOptionsFlowHandler(config_entries.OptionsFlow):
#     """Handle options."""

#     def __init__(self, config_entry):
#         """Initialize options flow."""
#         self.config_entry = config_entry

#     async def async_step_init(self, user_input=None):
#         """Manage the options."""
#         return await self.async_step_user_options(user_input)

#     async def async_step_user_options(self, user_input=None):
#         """Handle a flow initialized by the user."""
#         if user_input is not None:
#             return self.async_create_entry(title="", data=user_input)

#         return self.async_show_form(
#             step_id="user_options",
#             data_schema=vol.Schema(
#                 {
#                     # vol.Optional(CONF_USERNAME, default=self.config_entry.data.get(CONF_USERNAME)): str,
#                     # vol.Optional(CONF_PASSWORD, default=self.config_entry.data.get(CONF_PASSWORD)): str,
#                 }
#             ),
#         )

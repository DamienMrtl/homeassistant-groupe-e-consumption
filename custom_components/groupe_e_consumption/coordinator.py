import logging
from datetime import datetime, timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.event import async_track_time_change

from .api import GroupeEConsumptionAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EnergyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, session, username, password):
        """Initialize."""
        self.username = username
        self.password = password
        self.platforms = []
        self.session = session

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(days=1))

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        return []

    async def async_update_daily(self, now):
        """Fetch daily data at 3 AM."""
        _LOGGER.info("Fetching daily data")
        await self._fetch_data("daily")

    async def async_update_monthly(self, now):
        """Fetch monthly data on the 1st of each month at 3 AM."""
        _LOGGER.info("Fetching monthly data")
        await self._fetch_data("monthly")

    async def _fetch_data(self, resolution):
        """Fetch data from the API."""
        api = GroupeEConsumptionAPI(self.hass)
        token = await api.authenticate(self.username, self.password)
        if token:
            premise_id = await api.get_premise_id(token)
            partner_id = await api.get_partner_id(token)
            if resolution == "daily":
                start_timestamp = int(
                    (datetime.now() - timedelta(days=1)).timestamp() * 1000
                )
                end_timestamp = int(datetime.now().timestamp() * 1000)
            elif resolution == "monthly":
                start_timestamp = int(
                    (datetime.now().replace(day=1) - timedelta(days=1))
                    .replace(day=1)
                    .timestamp()
                    * 1000
                )
                end_timestamp = int(datetime.now().replace(day=1).timestamp() * 1000)
            data = await api.get_data(
                token,
                premise_id,
                partner_id,
                start_timestamp,
                end_timestamp,
                resolution,
            )
            self.data = data
        await api.close()

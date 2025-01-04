import logging
from datetime import datetime, timedelta
import pytz

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_change

from .api import GroupeEConsumptionAPI
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PREMISE_ID,
    CONF_PARTNER_ID,
)

_LOGGER = logging.getLogger(__name__)


class EnergyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, session, config_entry):
        """Initialize."""
        self.config_entry = config_entry
        self.platforms = []
        self.session = session
        self.daily_data = None
        self.monthly_data = None

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(days=1))

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        _LOGGER.info("Starting _async_update_data")

        _LOGGER.info(f"Current data: {self.data}")
        _LOGGER.info(f"Current daily_data: {self.daily_data}")
        _LOGGER.info(f"Current monthly_data: {self.monthly_data}")

        now = datetime.now(pytz.timezone("Europe/Zurich"))

        if (
            not self.daily_data
            or "last_reset" not in self.daily_data
            or self.daily_data["last_reset"].date() < (now - timedelta(days=1)).date()
        ):
            await self._fetch_data("daily")
        if (
            not self.monthly_data
            or "last_reset" not in self.monthly_data
            or self.monthly_data["last_reset"].date()
            < (now.replace(day=1) - timedelta(days=1)).date()
        ):
            await self._fetch_data("monthly")

    async def async_update_daily(self, now):
        """Fetch data at 3 AM."""
        _LOGGER.info("Fetching daily data")
        await self._fetch_data("daily")

        # Fetch monthly data on the first day of the month
        if now.day == 1:
            _LOGGER.info("Fetching monthly data")
            await self._fetch_data("monthly")

    async def _fetch_data(self, resolution):
        """Fetch data from the API."""
        _LOGGER.info(f"Fetching {resolution} data")
        username = self.config_entry.data[CONF_USERNAME]
        password = self.config_entry.data[CONF_PASSWORD]
        premise_id = self.config_entry.data[CONF_PREMISE_ID]
        partner_id = self.config_entry.data[CONF_PARTNER_ID]
        api = GroupeEConsumptionAPI(self.hass)
        token = await api.authenticate(username, password)
        if token:
            timezone = pytz.timezone("Europe/Zurich")
            today = datetime.now(timezone)
            today = today.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = today - timedelta(days=2)
            yesterday_timestamp = yesterday.timestamp() * 1000

            if resolution == "daily":
                # set start_timestamp to 00:00:00 of the yesterday
                start_timestamp = yesterday_timestamp
                end_timestamp = today.timestamp() * 1000
            elif resolution == "monthly":
                this_month = today.replace(day=1)
                last_month = this_month - timedelta(days=1)
                last_month = last_month.replace(day=1)

                start_timestamp = last_month.timestamp() * 1000
                end_timestamp = this_month.timestamp() * 1000

            _LOGGER.info(
                f"{resolution} start_timestamp: {start_timestamp}, end_timestamp: {end_timestamp}"
            )
            data = await api.get_data(
                token,
                premise_id,
                partner_id,
                int(start_timestamp),
                int(end_timestamp),
                resolution,
            )
            await api.close()
            if data:
                # _LOGGER.info(f"API response: {data}")

                # Check if there is data available in mesurementData
                if not data[0]["data"]["measurementData"]:
                    raise UpdateFailed("No data available in API response")

                # Extract values from the API response
                bas_tarif = data[0]["data"]["measurementData"][0]["value"]
                haut_tarif = data[1]["data"]["measurementData"][0]["value"]
                total = bas_tarif + haut_tarif
                last_reset = datetime.fromtimestamp(
                    data[0]["data"]["measurementData"][0]["timestamp"] / 1000, timezone
                )

                # Format the data as a dictionary and include the last_reset timestamp
                formatted_data = {
                    "total": total,
                    "bas_tarif": bas_tarif,
                    "haut_tarif": haut_tarif,
                    "last_reset": last_reset,
                }
                if resolution == "daily":
                    self.daily_data = formatted_data
                    _LOGGER.info(f"Updated daily_data: {self.daily_data}")
                elif resolution == "monthly":
                    self.monthly_data = formatted_data
                    _LOGGER.info(f"Updated monthly_data: {self.monthly_data}")

                self.data = {"updated": datetime.now()}
                return formatted_data
        await api.close()
        raise UpdateFailed("Failed to fetch data from API")

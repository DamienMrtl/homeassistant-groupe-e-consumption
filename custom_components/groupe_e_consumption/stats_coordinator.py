import logging
from datetime import datetime, timedelta
import pytz

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_change
from homeassistant.components.recorder.statistics import async_add_external_statistics
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData

from .api import GroupeEConsumptionAPI
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_PREMISE_ID,
    CONF_PARTNER_ID,
)

_LOGGER = logging.getLogger(__name__)


class StatsCoordinator(DataUpdateCoordinator):
    """Class to manage fetching quarter-hourly data from the API."""

    def __init__(self, hass, session, config_entry):
        """Initialize."""
        self.config_entry = config_entry
        self.platforms = []
        self.session = session

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(days=1))

    async def _async_update_data(self):
        """Fetch data from API endpoint."""

        now = datetime.now(pytz.timezone("Europe/Zurich"))
        await self.async_update_daily(now)

    async def async_update_daily(self, now):
        """Fetch data at 3 AM."""
        _LOGGER.info("Fetching quarter-hourly data")

        timezone = pytz.timezone("Europe/Zurich")
        today = datetime.now(timezone)
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        yesterday_timestamp = yesterday.timestamp() * 1000

        start_timestamp = yesterday_timestamp
        end_timestamp = today.timestamp() * 1000

        await self._fetch_data(start_timestamp, end_timestamp)

    async def _fetch_data(self, start_timestamp, end_timestamp):
        """Fetch data from the API."""
        _LOGGER.info(
            f"Fetching quarter-hourly data from {start_timestamp} to {end_timestamp}"
        )
        username = self.config_entry.data[CONF_USERNAME]
        password = self.config_entry.data[CONF_PASSWORD]
        premise_id = self.config_entry.data[CONF_PREMISE_ID]
        partner_id = self.config_entry.data[CONF_PARTNER_ID]
        api = GroupeEConsumptionAPI(self.hass)
        token = await api.authenticate(username, password)
        if token:
            data = await api.get_data(
                token,
                premise_id,
                partner_id,
                int(start_timestamp),
                int(end_timestamp),
                "quarter-hourly",
            )
            await api.close()
            if data:
                # Check if there is measurement data
                if "data" not in data[0] or "measurementData" not in data[0]["data"]:
                    raise UpdateFailed("No data available in API response")

                measurements = data[0]["data"]["measurementData"]

                # Prepare the data for the energy dashboard
                metadata = StatisticMetaData(
                    has_mean=False,
                    has_sum=False,
                    name="Quarter-Hourly Energy Consumption",
                    source="groupe_e_consumption",
                    statistic_id="groupe_e_consumption:quarter_hourly_energy_consumption",
                    unit_of_measurement="kWh",
                )

                # Temporary map to accumulate values for each hour
                temp_map = {}

                # Process each measurement
                for measurement in measurements:
                    # Convert timestamp to datetime and adjust to the start of the hour
                    timestamp = (measurement["timestamp"] / 1000) - (15 * 60)
                    timestamp = datetime.fromtimestamp(
                        timestamp, pytz.timezone("Europe/Zurich")
                    )
                    hour_start = timestamp.replace(minute=0, second=0, microsecond=0)

                    # Accumulate the values in the temp map
                    if hour_start in temp_map:
                        temp_map[hour_start] += measurement["value"]
                    else:
                        temp_map[hour_start] = measurement["value"]

                # Create statistics data from the temp map
                statistics_data = [
                    StatisticData(
                        start=hour_start,
                        state=value,
                        # sum=value,
                    )
                    for hour_start, value in temp_map.items()
                ]

                ## log the count of statistics data
                _LOGGER.info(f"Importing of statistics data: {len(statistics_data)}")

                # Add the data to the energy dashboard
                async_add_external_statistics(self.hass, metadata, statistics_data)
                # _LOGGER.info(
                #     f"Added quarter-hourly data to energy dashboard: {temp_map}"
                # )
        else:
            await api.close()
            raise UpdateFailed("Failed to fetch data from API")

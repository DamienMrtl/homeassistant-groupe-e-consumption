"""
Custom integration to get energy consumption data from an API.

For more details about this integration, please refer to
https://github.com/DamienMrtl/homeassistant-groupe-e-consumption
"""

import asyncio
import logging
from datetime import timedelta, datetime

import aiohttp
import async_timeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change

from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)
from .coordinator import EnergyDataUpdateCoordinator
from .stats_coordinator import StatsCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    session = async_get_clientsession(hass)
    coordinator = EnergyDataUpdateCoordinator(hass, session, entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][f"{entry.entry_id}_sensors"] = coordinator

    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            await hass.config_entries.async_forward_entry_setups(entry, [platform])

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Schedule daily update at 3 AM
    async_track_time_change(
        hass, coordinator.async_update_daily, hour=3, minute=0, second=0
    )

    # Set up the quarter-hourly coordinator
    stats_coordinator = StatsCoordinator(hass, session, entry)
    await stats_coordinator.async_refresh()

    if not stats_coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][f"{entry.entry_id}_stats"] = stats_coordinator

    # Schedule daily update at 3 AM for quarter-hourly data
    async_track_time_change(
        hass, stats_coordinator.async_update_daily, hour=3, minute=0, second=0
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    sensors_coordinator = hass.data[DOMAIN][f"{entry.entry_id}_sensors"]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in sensors_coordinator.platforms
            ]
        )
    )
    if unloaded:
        # Clean up the coordinator
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.data[DOMAIN].pop(f"{entry.entry_id}_sensors")
        hass.data[DOMAIN].pop(f"{entry.entry_id}_stats")

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

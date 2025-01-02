"""Platform for sensor integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENERGY_KILO_WATT_HOUR
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Groupe E Consumption sensor."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([GroupeEConsumptionSensor(coordinator)])


class GroupeEConsumptionSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_name = "Groupe E Consumption"
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self._coordinator = coordinator

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        return self._coordinator.data.get("kwh_consumed")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._coordinator.data

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def available(self):
        """Return if entity is available."""
        return self._coordinator.last_update_success

    async def async_added_to_hass(self):
        """When entity is added to hass."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        """Update the entity. Only used by the generic entity update service."""
        await self._coordinator.async_request_refresh()
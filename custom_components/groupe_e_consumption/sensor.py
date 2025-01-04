"""Platform for sensor integration."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EnergyDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Groupe E Consumption sensors."""
    coordinator = hass.data[DOMAIN][f"{config_entry.entry_id}_sensors"]
    async_add_entities(
        [
            DailyKwhConsumptionSensor(coordinator, config_entry.entry_id),
            MonthlyKwhConsumptionSensor(coordinator, config_entry.entry_id),
        ]
    )


class DailyKwhConsumptionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a daily kWh consumption sensor."""

    _attr_name = "Yesterday energy consumption"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_daily_kwh_consumption"
        self._state = None
        self._attributes = {}

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.daily_data.get("total")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "bas_tarif": self.coordinator.daily_data.get("bas_tarif"),
            "haut_tarif": self.coordinator.daily_data.get("haut_tarif"),
            "value_timestamp": self.coordinator.daily_data.get("last_reset"),
        }

    @property
    def last_reset(self):
        """Return the last reset timestamp."""
        return self.coordinator.daily_data.get("last_reset")


class MonthlyKwhConsumptionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a monthly kWh consumption sensor."""

    _attr_name = "Last month energy consumption"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(self, coordinator, entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_monthly_kwh_consumption"
        self._state = None
        self._attributes = {}

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.monthly_data.get("total")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "bas_tarif": self.coordinator.monthly_data.get("bas_tarif"),
            "haut_tarif": self.coordinator.monthly_data.get("haut_tarif"),
            "value_timestamp": self.coordinator.monthly_data.get("last_reset"),
        }

    @property
    def last_reset(self):
        """Return the last reset timestamp."""
        return self.coordinator.monthly_data.get("last_reset")

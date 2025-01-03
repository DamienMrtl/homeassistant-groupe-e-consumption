"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ENERGY_KILO_WATT_HOUR, POWER_KILO_WATT
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
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            DailyKwhConsumptionSensor(coordinator),
            MonthlyKwhConsumptionSensor(coordinator),
            FifteenMinuteKwSensor(coordinator),
        ]
    )


class DailyKwhConsumptionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a daily kWh consumption sensor."""

    _attr_name = "Daily kWh Consumption"
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = "energy"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._state = None
        self._attributes = {}

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("total")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "bas_tarif": self.coordinator.data.get("bas_tarif"),
            "haut_tarif": self.coordinator.data.get("haut_tarif"),
        }


class MonthlyKwhConsumptionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a monthly kWh consumption sensor."""

    _attr_name = "Monthly kWh Consumption"
    _attr_native_unit_of_measurement = ENERGY_KILO_WATT_HOUR
    _attr_device_class = "energy"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._state = None
        self._attributes = {}

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("total")

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "bas_tarif": self.coordinator.data.get("bas_tarif"),
            "haut_tarif": self.coordinator.data.get("haut_tarif"),
        }


class FifteenMinuteKwSensor(CoordinatorEntity, SensorEntity):
    """Representation of a 15-minute kW sensor."""

    _attr_name = "15-Minute kW"
    _attr_native_unit_of_measurement = POWER_KILO_WATT
    _attr_device_class = "power"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._state = None

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("power")

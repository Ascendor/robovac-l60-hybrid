from __future__ import annotations
import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, CONF_NAME, CONF_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_VACS, DOMAIN, REFRESH_RATE

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=REFRESH_RATE)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eufy Robovac sensor entities."""
    vacuums = config_entry.data[CONF_VACS]
    entities: list[SensorEntity] = []

    for vacuum_id in vacuums:
        item = vacuums[vacuum_id]
        entities.append(RobovacBatterySensor(item))

    async_add_entities(entities)

class RobovacBatterySensor(SensorEntity):
    """Representation of a Robovac battery sensor."""
    _attr_has_entity_name = True
    _attr_name = "Battery"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_available = False

    def __init__(self, item: dict[str, Any]) -> None:
        """Initialize the sensor."""
        self._robovac_id = item[CONF_ID]
        self._attr_unique_id = f"{item[CONF_ID]}_battery"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, item[CONF_ID])},
            name=item[CONF_NAME],
        )

    async def async_update(self) -> None:
        """Update the sensor state."""
        try:
            vacuum_entity = self.hass.data[DOMAIN][CONF_VACS].get(self._robovac_id)
            if vacuum_entity is not None:
                battery_level = vacuum_entity.battery_level
                if battery_level is not None:
                    self._attr_native_value = battery_level
                    self._attr_available = True
                else:
                    self._attr_available = False
            else:
                self._attr_available = False
        except Exception:
            _LOGGER.debug("Failed to get battery level for %s", self._robovac_id)
            self._attr_native_value = None
            self._attr_available = False
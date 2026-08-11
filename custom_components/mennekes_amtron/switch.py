from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .coordinator import MennekesAmtronCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: MennekesAmtronCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MennekesAvailabilitySwitch(coordinator)])


class MennekesAvailabilitySwitch(SwitchEntity):
    _attr_name = "MENNEKES Charging available"

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.host}_charging_available"

    @property
    def is_on(self):
        return bool(self.coordinator.data) and self.coordinator.data["availability"]

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_turn_on(self, **kwargs):
        await self.coordinator.async_set_availability(True)

    async def async_turn_off(self, **kwargs):
        await self.coordinator.async_set_availability(False)

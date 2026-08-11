from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfElectricCurrent

from .const import DOMAIN
from .coordinator import MennekesAmtronCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: MennekesAmtronCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MennekesHemsLimitNumber(coordinator)])


class MennekesHemsLimitNumber(NumberEntity):
    _attr_name = "MENNEKES HEMS current limit"
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_native_min_value = 0
    _attr_native_max_value = 32
    _attr_native_step = 1
    _attr_mode = "slider"

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.host}_hems_current_limit"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("hems_current_a")

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_hems_current(int(value))

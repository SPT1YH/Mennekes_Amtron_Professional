"""Number controls for MENNEKES AMTRON."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.const import UnitOfElectricCurrent

from .const import MAX_CHARGING_CURRENT
from .coordinator import MennekesCoordinator
from .entity import MennekesEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: MennekesCoordinator = entry.runtime_data
    async_add_entities([MennekesCurrentLimitNumber(coordinator)])


class MennekesCurrentLimitNumber(MennekesEntity, NumberEntity):
    """HEMS current limit, register 1000."""

    _attr_name = "HEMS charging current"
    _attr_native_min_value = 0
    _attr_native_max_value = MAX_CHARGING_CURRENT
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: MennekesCoordinator) -> None:
        super().__init__(coordinator, "hems_current_limit")

    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = min(
            max(self.coordinator.data["hems_current_limit"], 0),
            MAX_CHARGING_CURRENT,
        )
        super()._handle_coordinator_update()

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_current_limit(round(value))
        self._attr_native_value = round(value)
        self.async_write_ha_state()

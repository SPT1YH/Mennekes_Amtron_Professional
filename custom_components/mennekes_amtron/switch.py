"""Switch controls for MENNEKES AMTRON."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .coordinator import MennekesCoordinator
from .entity import MennekesEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: MennekesCoordinator = entry.runtime_data
    async_add_entities([MennekesAvailabilitySwitch(coordinator)])


class MennekesAvailabilitySwitch(MennekesEntity, SwitchEntity):
    """Control CP availability via register 124.

    For firmware >= 5.22, MENNEKES defines 1 as available and 0 as unavailable.
    """

    _attr_name = "Charging available"

    def __init__(self, coordinator: MennekesCoordinator) -> None:
        super().__init__(coordinator, "availability")

    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = bool(self.coordinator.data["availability"])
        super()._handle_coordinator_update()

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_availability(True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_availability(False)

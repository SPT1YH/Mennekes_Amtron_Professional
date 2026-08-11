"""Binary sensors for MENNEKES AMTRON."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from .coordinator import MennekesCoordinator
from .entity import MennekesEntity


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: MennekesCoordinator = entry.runtime_data
    async_add_entities(
        [
            MennekesErrorSensor(coordinator),
            MennekesPlugSensor(coordinator),
            MennekesChargingSensor(coordinator),
        ]
    )


class MennekesErrorSensor(MennekesEntity, BinarySensorEntity):
    """Indicate whether any documented ECU error is active."""

    _attr_name = "Error"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: MennekesCoordinator) -> None:
        super().__init__(coordinator, "error")

    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = bool(self.coordinator.data["error_mask"])
        super()._handle_coordinator_update()


class MennekesPlugSensor(MennekesEntity, BinarySensorEntity):
    """Indicate whether the plug is locked."""

    _attr_name = "Plug locked"
    _attr_device_class = BinarySensorDeviceClass.LOCK

    def __init__(self, coordinator: MennekesCoordinator) -> None:
        super().__init__(coordinator, "plug_locked")

    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["plug_locked"]
        super()._handle_coordinator_update()


class MennekesChargingSensor(MennekesEntity, BinarySensorEntity):
    """Indicate whether the charge point is actively charging."""

    _attr_name = "Charging"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, coordinator: MennekesCoordinator) -> None:
        super().__init__(coordinator, "charging")

    def _handle_coordinator_update(self) -> None:
        self._attr_is_on = self.coordinator.data["status"] == 6
        super()._handle_coordinator_update()

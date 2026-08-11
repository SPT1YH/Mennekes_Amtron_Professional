from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from .const import DOMAIN
from .coordinator import MennekesAmtronCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: MennekesAmtronCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            MennekesOnlineSensor(coordinator),
            MennekesChargingSensor(coordinator),
            MennekesPlugLockedSensor(coordinator),
            MennekesErrorSensor(coordinator),
        ]
    )


class _Base(MennekesAmtronCoordinator, BinarySensorEntity):
    pass


class MennekesOnlineSensor(BinarySensorEntity):
    _attr_name = "MENNEKES Modbus online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.host}_modbus_online"

    @property
    def is_on(self):
        return self.coordinator.last_update_success

    @property
    def available(self):
        return True


class MennekesChargingSensor(BinarySensorEntity):
    _attr_name = "MENNEKES Charging"
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.host}_charging"

    @property
    def is_on(self):
        return bool(self.coordinator.data) and self.coordinator.data["status"] == 6

    @property
    def available(self):
        return self.coordinator.last_update_success


class MennekesPlugLockedSensor(BinarySensorEntity):
    _attr_name = "MENNEKES Plug locked"
    _attr_device_class = BinarySensorDeviceClass.LOCK

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.host}_plug_locked"

    @property
    def is_on(self):
        return bool(self.coordinator.data) and self.coordinator.data["plug_locked"]

    @property
    def available(self):
        return self.coordinator.last_update_success


class MennekesErrorSensor(BinarySensorEntity):
    _attr_name = "MENNEKES Error"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.host}_error"

    @property
    def is_on(self):
        return bool(self.coordinator.data) and bool(
            self.coordinator.data["error_word_1"]
        )

    @property
    def available(self):
        return self.coordinator.last_update_success

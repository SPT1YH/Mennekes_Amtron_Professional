from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)

from .const import DOMAIN
from .coordinator import MennekesAmtronCoordinator


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        MennekesValueSensor(coordinator, "status_name", "Status", None),
        MennekesValueSensor(coordinator, "vehicle_state_name", "Vehicle state", None),
        MennekesValueSensor(coordinator, "firmware", "Firmware", None),
        MennekesValueSensor(coordinator, "protocol_version", "Modbus protocol", None),
        MennekesValueSensor(coordinator, "model", "Model", None),
        MennekesValueSensor(coordinator, "hems_current_a", "HEMS current limit", UnitOfElectricCurrent.AMPERE),
        MennekesValueSensor(coordinator, "signaled_current_a", "Signalled current", UnitOfElectricCurrent.AMPERE),
        MennekesValueSensor(coordinator, "minimum_current_a", "Minimum current", UnitOfElectricCurrent.AMPERE),
        MennekesValueSensor(coordinator, "max_ev_current_a", "Maximum EV current", UnitOfElectricCurrent.AMPERE),
        MennekesValueSensor(coordinator, "total_power_w", "Total power", UnitOfPower.WATT, SensorDeviceClass.POWER),
        MennekesValueSensor(coordinator, "total_energy_wh", "Total energy", UnitOfEnergy.WATT_HOUR, SensorDeviceClass.ENERGY),
        MennekesValueSensor(coordinator, "power_l1_w", "Power L1", UnitOfPower.WATT, SensorDeviceClass.POWER),
        MennekesValueSensor(coordinator, "power_l2_w", "Power L2", UnitOfPower.WATT, SensorDeviceClass.POWER),
        MennekesValueSensor(coordinator, "power_l3_w", "Power L3", UnitOfPower.WATT, SensorDeviceClass.POWER),
        MennekesValueSensor(coordinator, "current_l1_a", "Current L1", UnitOfElectricCurrent.AMPERE),
        MennekesValueSensor(coordinator, "current_l2_a", "Current L2", UnitOfElectricCurrent.AMPERE),
        MennekesValueSensor(coordinator, "current_l3_a", "Current L3", UnitOfElectricCurrent.AMPERE),
        MennekesValueSensor(coordinator, "voltage_l1_v", "Voltage L1", UnitOfElectricPotential.VOLT),
        MennekesValueSensor(coordinator, "voltage_l2_v", "Voltage L2", UnitOfElectricPotential.VOLT),
        MennekesValueSensor(coordinator, "voltage_l3_v", "Voltage L3", UnitOfElectricPotential.VOLT),
        MennekesValueSensor(coordinator, "session_energy_wh", "Session energy", UnitOfEnergy.WATT_HOUR, SensorDeviceClass.ENERGY),
        MennekesValueSensor(coordinator, "session_duration_s", "Session duration", UnitOfTime.SECONDS),
        MennekesValueSensor(coordinator, "safe_current_a", "Safe current", UnitOfElectricCurrent.AMPERE),
        MennekesValueSensor(coordinator, "comm_timeout_s", "Modbus communication timeout", UnitOfTime.SECONDS),
        MennekesValueSensor(coordinator, "operator_current_a", "Operator current limit", UnitOfElectricCurrent.AMPERE),
    ]

    async_add_entities(entities)


class MennekesValueSensor(SensorEntity):
    def __init__(self, coordinator, key, name, unit, device_class=None):
        self.coordinator = coordinator
        self.key = key
        self._attr_name = f"MENNEKES {name}"
        self._attr_unique_id = f"{coordinator.host}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = (
            SensorStateClass.TOTAL_INCREASING
            if key in {"total_energy_wh", "session_energy_wh"}
            else None
        )

    @property
    def native_value(self):
        return self.coordinator.data.get(self.key) if self.coordinator.data else None

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

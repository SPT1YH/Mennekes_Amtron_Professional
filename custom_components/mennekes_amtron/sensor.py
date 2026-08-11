"""Sensors for MENNEKES AMTRON."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.const import UnitOfElectricCurrent, UnitOfEnergy, UnitOfPower, UnitOfElectricPotential, UnitOfTime
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_NAMES, VEHICLE_STATE_NAMES
from .coordinator import MennekesCoordinator
from .entity import MennekesEntity


@dataclass(frozen=True, kw_only=True)
class MennekesSensorDescription(SensorEntityDescription):
    value_fn: Any
    unit: str | None = None


SENSORS = (
    MennekesSensorDescription(key="status", name="Status", value_fn=lambda d: STATUS_NAMES.get(d["status"], f"Unknown ({d['status']})")),
    MennekesSensorDescription(key="vehicle_state", name="Vehicle state", value_fn=lambda d: VEHICLE_STATE_NAMES.get(d["vehicle_state"], f"Unknown ({d['vehicle_state']})")),
    MennekesSensorDescription(key="firmware", name="Firmware", value_fn=lambda d: d["firmware"], entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="model", name="Model", value_fn=lambda d: d["model"], entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="protocol_version", name="Modbus protocol version", value_fn=lambda d: d["protocol_version"], entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="total_power", name="Total power", value_fn=lambda d: d["total_power"] / 1000, unit=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="power_l1", name="Power L1", value_fn=lambda d: d["power_l1"] / 1000, unit=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="power_l2", name="Power L2", value_fn=lambda d: d["power_l2"] / 1000, unit=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="power_l3", name="Power L3", value_fn=lambda d: d["power_l3"] / 1000, unit=UnitOfPower.KILO_WATT, device_class=SensorDeviceClass.POWER, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="total_energy", name="Total energy", value_fn=lambda d: d["total_energy"] / 1000, unit=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),
    MennekesSensorDescription(key="energy_l1", name="Energy L1", value_fn=lambda d: d["energy_l1"] / 1000, unit=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),
    MennekesSensorDescription(key="energy_l2", name="Energy L2", value_fn=lambda d: d["energy_l2"] / 1000, unit=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),
    MennekesSensorDescription(key="energy_l3", name="Energy L3", value_fn=lambda d: d["energy_l3"] / 1000, unit=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY, state_class=SensorStateClass.TOTAL_INCREASING),
    MennekesSensorDescription(key="current_l1", name="Current L1", value_fn=lambda d: d["current_l1"] / 1000, unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="current_l2", name="Current L2", value_fn=lambda d: d["current_l2"] / 1000, unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="current_l3", name="Current L3", value_fn=lambda d: d["current_l3"] / 1000, unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="voltage_l1", name="Voltage L1", value_fn=lambda d: d["voltage_l1"], unit=UnitOfVoltage.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="voltage_l2", name="Voltage L2", value_fn=lambda d: d["voltage_l2"], unit=UnitOfVoltage.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="voltage_l3", name="Voltage L3", value_fn=lambda d: d["voltage_l3"], unit=UnitOfVoltage.VOLT, device_class=SensorDeviceClass.VOLTAGE, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="charged_energy", name="Charged energy", value_fn=lambda d: d["charged_energy"] / 1000, unit=UnitOfEnergy.KILO_WATT_HOUR, device_class=SensorDeviceClass.ENERGY),
    MennekesSensorDescription(key="charge_duration", name="Charge duration", value_fn=lambda d: d["charge_duration"], unit=UnitOfTime.SECONDS, device_class=SensorDeviceClass.DURATION),
    MennekesSensorDescription(key="signalled_current", name="Signalled current", value_fn=lambda d: d["signalled_current"], unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="max_current_ev", name="EV maximum current", value_fn=lambda d: d["max_current_ev"], unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="minimum_current", name="Minimum charging current", value_fn=lambda d: d["minimum_current"], unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="operator_current_limit", name="Operator current limit", value_fn=lambda d: d["operator_current_limit"], unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, state_class=SensorStateClass.MEASUREMENT),
    MennekesSensorDescription(key="safe_current", name="Safe current", value_fn=lambda d: d["safe_current"], unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="dlm_mode", name="DLM mode", value_fn=lambda d: d["dlm_mode"], entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="dlm_available_l1", name="DLM available L1", value_fn=lambda d: d["dlm_available_l1"], unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="dlm_available_l2", name="DLM available L2", value_fn=lambda d: d["dlm_available_l2"], unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="dlm_available_l3", name="DLM available L3", value_fn=lambda d: d["dlm_available_l3"], unit=UnitOfElectricCurrent.AMPERE, device_class=SensorDeviceClass.CURRENT, entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="idtag", name="Current ID tag", value_fn=lambda d: d["idtag"], entity_category=EntityCategory.DIAGNOSTIC),
    MennekesSensorDescription(key="evccid", name="EVCC ID", value_fn=lambda d: d["evccid"], entity_category=EntityCategory.DIAGNOSTIC),
)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: MennekesCoordinator = entry.runtime_data
    async_add_entities(MennekesSensor(coordinator, description) for description in SENSORS)


class MennekesSensor(MennekesEntity, SensorEntity):
    """A MENNEKES sensor."""

    entity_description: MennekesSensorDescription

    def __init__(self, coordinator: MennekesCoordinator, description: MennekesSensorDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_entity_category = description.entity_category

    def _handle_coordinator_update(self) -> None:
        self._attr_native_value = self.entity_description.value_fn(self.coordinator.data)
        super()._handle_coordinator_update()

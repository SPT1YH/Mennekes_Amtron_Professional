# custom_components/mennekes_amtron/sensor.py
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfElectricCurrent, UnitOfEnergy, UnitOfPower, UnitOfElectricPotential, UnitOfTime
from .const import DOMAIN
from .coordinator import MennekesAmtronCoordinator

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MennekesHemsLimitSensor(coordinator)])

class MennekesHemsLimitSensor(SensorEntity):
    def __init__(self, coordinator: MennekesAmtronCoordinator):
        self.coordinator = coordinator
        self._attr_name = "MENNEKES HEMS Stromlimit"
        self._attr_unique_id = f"{coordinator.host}_hems_stromlimit"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get("hems_stromlimit")
        return None

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self):
        await self.coordinator.async_request_refresh()
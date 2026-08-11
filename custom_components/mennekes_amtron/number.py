# custom_components/mennekes_amtron/number.py
import logging
from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfElectricCurrent
from .const import DOMAIN
from .coordinator import MennekesAmtronCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MennekesHemsLimitNumber(coordinator)])

class MennekesHemsLimitNumber(NumberEntity):
    def __init__(self, coordinator: MennekesAmtronCoordinator):
        self.coordinator = coordinator
        self._attr_name = "MENNEKES HEMS Stromlimit Setzen"
        self._attr_unique_id = f"{coordinator.host}_hems_stromlimit_number"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_native_min_value = 0
        self._attr_native_max_value = 32
        self._attr_native_step = 1

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get("hems_stromlimit")
        return None

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_set_native_value(self, value: float) -> None:
        from pymodbus.client import AsyncModbusTcpClient
        client = AsyncModbusTcpClient(self.coordinator.host, port=self.coordinator.port)
        try:
            connected = await client.connect()
            if not connected:
                _LOGGER.error("Modbus-Verbindung zum Schreiben des Limits fehlgeschlagen.")
                return

            result = await client.write_register(
                address=1000, 
                value=int(value), 
                device_id=self.coordinator.slave_id
            )
            
            if result.isError():
                _LOGGER.error(f"Fehler beim Schreiben auf Register 1000: {result}")
            else:
                _LOGGER.info(f"Erfolgreich HEMS-Limit auf {int(value)} A gesetzt.")

            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(f"Exception beim Schreiben des Modbus-Registers: {err}")
        finally:
            client.close()

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
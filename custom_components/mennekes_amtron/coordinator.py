import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

_LOGGER = logging.getLogger(__name__)

class MennekesAmtronCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host, port=502, slave_id=1):
        super().__init__(
            hass,
            _LOGGER,
            name="MENNEKES AMTRON",
            update_interval=timedelta(seconds=10),
        )
        self.host = host
        self.port = port
        self.slave_id = slave_id

    async def _async_update_data(self):
        client = AsyncModbusTcpClient(self.host, port=self.port)
        
        try:
            connected = await client.connect()
            if not connected:
                raise UpdateFailed(f"Verbindung zu {self.host}:{self.port} fehlgeschlagen.")

            # Korrektur: device_id statt slave verwenden
            response = await client.read_holding_registers(
                address=1000, 
                count=1, 
                device_id=self.slave_id
            )
            
            if response.isError():
                raise UpdateFailed(f"Modbus-Fehler (Response Error): {response}")

            return {
                "hems_stromlimit": response.registers[0]
            }

        except ModbusException as err:
            raise UpdateFailed(f"Modbus-Verbindungsabbruch: {err}")
        except Exception as err:
            raise UpdateFailed(f"Unerwarteter Fehler: {err}")
        finally:
            client.close()
# custom_components/mennekes_amtron/config_flow.py
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from .const import DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=502): int,
    }
)

class MennekesAmtronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            client = AsyncModbusTcpClient(
                user_input[CONF_HOST], port=user_input[CONF_PORT]
            )
            try:
                connected = await client.connect()
                if not connected:
                    errors["base"] = "cannot_connect"
                else:
                    result = await client.read_holding_registers(
                        address=1000, count=1, slave=1
                    )
                    if result.isError():
                        errors["base"] = "read_error"
                    else:
                        return self.async_create_entry(
                            title=f"MENNEKES ({user_input[CONF_HOST]})",
                            data=user_input,
                        )
            except ModbusException:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            finally:
                client.close()

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
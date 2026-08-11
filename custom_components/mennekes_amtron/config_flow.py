from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT

from .api import MennekesModbusClient, ModbusError
from .const import DEFAULT_PORT, DOMAIN

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): vol.All(
            int, vol.Range(min=1, max=65535)
        ),
    }
)


class MennekesAmtronConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            client = MennekesModbusClient(
                user_input[CONF_HOST],
                port=user_input[CONF_PORT],
                unit_id=1,
                timeout=5,
            )

            try:
                # Do NOT read register 1000 here.  The first test is a documented
                # read-only system register block.
                registers = await client.read_holding_registers(100, 5)

                if len(registers) != 5:
                    errors["base"] = "read_error"
                else:
                    await self.async_set_unique_id(
                        f"mennekes_amtron_{user_input[CONF_HOST]}"
                    )
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"MENNEKES ({user_input[CONF_HOST]})",
                        data=user_input,
                    )

            except ModbusError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )

# MENNEKES AMTRON Professional for Home Assistant

Local Home Assistant custom integration for MENNEKES AMTRON Professional wallboxes using the documented MENNEKES Modbus TCP interface.

## Requirements

On the wallbox enable:

- Modbus TCP Server: **On**
- Base Port: **502** (or the configured port)
- Register Address Set: **MENNEKES**
- Allow Start/Stop Transaction: **On** if transaction controls are later added

The integration uses raw Modbus TCP and therefore does not depend on `pymodbus`.

## Current entities (v0.1)

- Wallbox status and vehicle state
- Firmware/model/protocol diagnostics
- Total and per-phase power, energy, current and voltage
- Current session energy and duration
- Signalled/EV/minimum/operator/safe currents
- DLM diagnostics
- Plug lock, charging and error binary sensors
- HEMS charging-current number (register 1000)
- Charging-availability switch (register 124; firmware >= 5.22 semantics)

## Important

The HEMS current limit is an EMS control value. The actual signalled current can be lower because of cable and DLM limits. Setting register 1000 to 0 pauses the charging session according to the MENNEKES specification.

This project is not affiliated with MENNEKES.

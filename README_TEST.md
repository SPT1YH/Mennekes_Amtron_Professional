# MENNEKES AMTRON Professional v0.2.0 – Teststand

This version deliberately removes pymodbus and uses the raw Modbus TCP client in `api.py`.

## Installation

Copy `custom_components/mennekes_amtron` to `/config/custom_components/`.

Restart Home Assistant.

## Wallbox

- Modbus TCP Server: On
- Base Port: 502
- Register Address Set: MENNEKES
- Unit ID: the integration uses 1 (MENNEKES says the server accepts 1..255)

## What changed

The first connection test reads registers 100..104. It does NOT read register 1000 as a health check.

The coordinator then reads:
- 100..152 general information
- 200..227 meter values
- 716..719 session data
- 706..715 charge data
- 131..134 configuration
- 1000 HEMS current limit

Debug logging is included at the raw Modbus frame level.

## Enable logging

Add to configuration.yaml:

```yaml
logger:
  default: warning
  logs:
    custom_components.mennekes_amtron: debug
```

After restart, look for:

`MENNEKES Modbus TCP TX ...`

and

`MENNEKES Modbus TCP RX ...`

If the connection is successful, the integration should show:
- MENNEKES Modbus online = On
- MENNEKES Status
- MENNEKES Vehicle state
- MENNEKES Firmware
- MENNEKES Total power
- etc.

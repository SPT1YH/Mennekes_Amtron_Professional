from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import MennekesModbusClient, ModbusError
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT_ID,
    STATUS_NAMES,
    VEHICLE_STATE_NAMES,
)

_LOGGER = logging.getLogger(__name__)

# MENNEKES ECU register addresses are used directly as documented.
REG_FIRMWARE = 100          # 2 registers
REG_STATUS = 104            # 1
REG_ERROR = 105             # 2 registers (first 32-bit error word)
REG_PROTOCOL = 120          # 2
REG_VEHICLE = 122           # 1
REG_AVAILABILITY = 124      # 1
REG_MODEL = 142             # 10 registers
REG_PLUG_LOCK = 152         # 1

REG_ENERGY_L1 = 200         # 2
REG_ENERGY_L2 = 202         # 2
REG_ENERGY_L3 = 204         # 2
REG_POWER_L1 = 206          # 2
REG_POWER_L2 = 208          # 2
REG_POWER_L3 = 210          # 2
REG_CURRENT_L1 = 212        # 2, mA
REG_CURRENT_L2 = 214        # 2, mA
REG_CURRENT_L3 = 216        # 2, mA
REG_TOTAL_ENERGY = 218      # 2, Wh
REG_TOTAL_POWER = 220       # 2, W
REG_VOLTAGE_L1 = 222        # 2, V
REG_VOLTAGE_L2 = 224        # 2, V
REG_VOLTAGE_L3 = 226        # 2, V

REG_SESSION_ENERGY = 716    # 2, Wh, firmware >= 5.22
REG_SESSION_DURATION = 718  # 2, seconds, firmware >= 5.22
REG_SIGNALED_CURRENT = 706  # 1, A
REG_MIN_CURRENT = 712       # 1, A
REG_MAX_EV_CURRENT = 715    # 1, A
REG_HEMS_CURRENT = 1000     # 1, R/W, A

REG_SAFE_CURRENT = 131      # 1, A
REG_COMM_TIMEOUT = 132     # 1, seconds
REG_OPERATOR_CURRENT = 134  # 1, A

REG_DLM_MODE = 600          # 1


def _u32(registers: list[int]) -> int:
    if len(registers) != 2:
        raise ValueError("Expected two registers for uint32")
    return (registers[0] << 16) | registers[1]


def _ascii(registers: list[int]) -> str:
    raw = b"".join(int(r).to_bytes(2, "big") for r in registers)
    return raw.decode("ascii", errors="replace").replace("\x00", "").strip()


# Import locally to keep helper dependency obvious.
import struct


class MennekesAmtronCoordinator(DataUpdateCoordinator[dict]):
    """Poll the documented MENNEKES ECU Modbus register set."""

    def __init__(
        self,
        hass,
        host: str,
        port: int = 502,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
        unit_id: int = DEFAULT_UNIT_ID,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = DEFAULT_TIMEOUT

        self.client = MennekesModbusClient(
            host,
            port=port,
            unit_id=unit_id,
            timeout=self.timeout,
        )

        super().__init__(
            hass,
            _LOGGER,
            name="MENNEKES AMTRON Professional",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _read_block(self, start: int, count: int) -> list[int]:
        return await self.client.read_holding_registers(start, count)

    async def _async_update_data(self) -> dict:
        """Read only safe/readable registers. No write/control register is used as a health check."""
        try:
            # First read: small, always-readable general-system block.
            # This is deliberately the connectivity/health check.
            general = await self._read_block(REG_FIRMWARE, 53)  # 100..152

            def g(addr: int, count: int = 1) -> list[int]:
                start = addr - REG_FIRMWARE
                return general[start : start + count]

            status = g(REG_STATUS)[0]
            vehicle = g(REG_VEHICLE)[0]
            availability = g(REG_AVAILABILITY)[0]
            plug_lock = g(REG_PLUG_LOCK)[0]

            firmware_raw = g(REG_FIRMWARE, 2)
            protocol_raw = g(REG_PROTOCOL, 2)
            model_raw = g(REG_MODEL, 10)

            # Meter block.
            meter = await self._read_block(REG_ENERGY_L1, 28)

            def m(addr: int, count: int = 2) -> list[int]:
                start = addr - REG_ENERGY_L1
                return meter[start : start + count]

            # Charge-process block.
            charge = await self._read_block(REG_SESSION_ENERGY, 4)
            process = await self._read_block(REG_SIGNALED_CURRENT, 10)

            # Configuration/HEMS registers. 1000 is R/W according to MENNEKES,
            # but it is only read after the connection has already been proven.
            control = await self._read_block(REG_SAFE_CURRENT, 4)
            hems = await self._read_block(REG_HEMS_CURRENT, 1)

            return {
                "status": status,
                "status_name": STATUS_NAMES.get(status, f"Unknown ({status})"),
                "vehicle_state": vehicle,
                "vehicle_state_name": VEHICLE_STATE_NAMES.get(
                    vehicle, f"Unknown ({vehicle})"
                ),
                "availability": bool(availability),
                "plug_locked": bool(plug_lock),
                "firmware": _ascii(firmware_raw),
                "protocol_version": _ascii(protocol_raw),
                "model": _ascii(model_raw),
                "error_word_1": _u32(g(REG_ERROR, 2)),
                "energy_l1_wh": _u32(m(REG_ENERGY_L1)),
                "energy_l2_wh": _u32(m(REG_ENERGY_L2)),
                "energy_l3_wh": _u32(m(REG_ENERGY_L3)),
                "total_energy_wh": _u32(m(REG_TOTAL_ENERGY)),
                "power_l1_w": _u32(m(REG_POWER_L1)),
                "power_l2_w": _u32(m(REG_POWER_L2)),
                "power_l3_w": _u32(m(REG_POWER_L3)),
                "total_power_w": _u32(m(REG_TOTAL_POWER)),
                "current_l1_a": _u32(m(REG_CURRENT_L1)) / 1000,
                "current_l2_a": _u32(m(REG_CURRENT_L2)) / 1000,
                "current_l3_a": _u32(m(REG_CURRENT_L3)) / 1000,
                "voltage_l1_v": _u32(m(REG_VOLTAGE_L1)),
                "voltage_l2_v": _u32(m(REG_VOLTAGE_L2)),
                "voltage_l3_v": _u32(m(REG_VOLTAGE_L3)),
                "session_energy_wh": _u32(charge[0:2]),
                "session_duration_s": _u32(charge[2:4]),
                "signaled_current_a": process[0],
                "minimum_current_a": process[6],
                "max_ev_current_a": process[9],
                "safe_current_a": control[0],
                "comm_timeout_s": control[1],
                "operator_current_a": control[3],
                "hems_current_a": hems[0],
                "online": True,
            }

        except ModbusError as err:
            _LOGGER.error(
                "MENNEKES Modbus read failed (%s:%s, unit=%s): %s",
                self.host,
                self.port,
                self.unit_id,
                err,
            )
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            _LOGGER.exception("Unexpected MENNEKES coordinator error")
            raise UpdateFailed(str(err)) from err

    async def async_set_hems_current(self, value: int) -> None:
        """Write HEMS_CURRENT_LIMIT (register 1000)."""
        if value != 0 and not 6 <= value <= 32:
            raise ValueError("HEMS current must be 0 or 6..32 A")

        await self.client.write_single_register(REG_HEMS_CURRENT, int(value))
        await self.async_request_refresh()

    async def async_set_availability(self, available: bool) -> None:
        """Write CP_AVAILABILITY (register 124). Firmware >= 5.22: 1=available."""
        await self.client.write_single_register(REG_AVAILABILITY, 1 if available else 0)
        await self.async_request_refresh()

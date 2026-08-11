"""Data coordinator for MENNEKES AMTRON."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MennekesModbusClient, ModbusError
from .const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


def _u32(registers: dict[int, int], address: int) -> int:
    """Decode a documented 32-bit big-endian register pair."""
    return (registers[address] << 16) | registers[address + 1]


def _u32_or_none(registers: dict[int, int], address: int) -> int | None:
    """Decode a meter value, mapping MENNEKES 0xFFFFFFFF to unavailable."""
    value = _u32(registers, address)
    return None if value == 0xFFFFFFFF else value


def _ascii_u32(registers: dict[int, int], address: int, count_32: int) -> str:
    raw = bytearray()
    for offset in range(count_32):
        raw.extend(_u32(registers, address + offset * 2).to_bytes(4, "big"))
    return raw.decode("ascii", errors="replace").rstrip("\x00 ")


def _error_u32(registers: dict[int, int], address: int) -> int:
    """Decode one of MENNEKES' error-mask 32-bit pairs.

    Error registers are the documented exception to normal word/byte ordering.
    """
    a = registers[address]
    b = registers[address + 1]
    a = ((a & 0xFF) << 8) | (a >> 8)
    b = ((b & 0xFF) << 8) | (b >> 8)
    return (b << 16) | a


class MennekesCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll the MENNEKES ECU in a single coordinated update."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.client = MennekesModbusClient(
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
        )
        interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
            always_update=False,
        )

    async def _read_range(self, registers: dict[int, int], start: int, count: int) -> None:
        values = await self.client.read_holding_registers(start, count)
        registers.update({start + index: value for index, value in enumerate(values)})

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            registers: dict[int, int] = {}
            # Keep each read below the Modbus maximum of 125 registers and avoid gaps.
            for start, count in (
                (100, 25),
                (130, 23),
                (200, 28),
                (600, 36),
                (700, 47),
                (1000, 1),
            ):
                await self._read_range(registers, start, count)

            data: dict[str, Any] = {
                "firmware": _ascii_u32(registers, 100, 1),
                "status": registers[104],
                "error_mask": (
                    _error_u32(registers, 105)
                    | (_error_u32(registers, 107) << 32)
                    | (_error_u32(registers, 109) << 64)
                    | (_error_u32(registers, 111) << 96)
                ),
                "protocol_version": _ascii_u32(registers, 120, 1),
                "vehicle_state": registers[122],
                "availability": registers[124],
                "safe_current": registers[131],
                "communication_timeout": registers[132],
                "operator_current_limit": registers[134],
                "model": _ascii_u32(registers, 142, 5),
                "plug_locked": registers[152] == 1,
                "energy_l1": _u32_or_none(registers, 200),
                "energy_l2": _u32_or_none(registers, 202),
                "energy_l3": _u32_or_none(registers, 204),
                "power_l1": _u32_or_none(registers, 206),
                "power_l2": _u32_or_none(registers, 208),
                "power_l3": _u32_or_none(registers, 210),
                "current_l1": _u32_or_none(registers, 212),
                "current_l2": _u32_or_none(registers, 214),
                "current_l3": _u32_or_none(registers, 216),
                "total_energy": _u32_or_none(registers, 218),
                "total_power": _u32_or_none(registers, 220),
                "voltage_l1": _u32_or_none(registers, 222),
                "voltage_l2": _u32_or_none(registers, 224),
                "voltage_l3": _u32_or_none(registers, 226),
                "dlm_mode": registers[600],
                "dlm_limit_l1": registers[610],
                "dlm_limit_l2": registers[611],
                "dlm_limit_l3": registers[612],
                "dlm_applied_l1": registers[630],
                "dlm_applied_l2": registers[631],
                "dlm_applied_l3": registers[632],
                "dlm_available_l1": registers[633],
                "dlm_available_l2": registers[634],
                "dlm_available_l3": registers[635],
                "required_energy_15118": registers[700],
                "charged_energy": _u32(registers, 716),
                "signalled_current": registers[706],
                "start_time": _u32(registers, 707),
                "charge_duration": _u32(registers, 718),
                "end_time": _u32(registers, 710),
                "minimum_current": registers[712],
                "hems_current_limit": registers[1000],
                "max_current_ev": registers[715],
                "idtag": _ascii_u32(registers, 720, 5),
                "evccid": _ascii_u32(registers, 741, 3),
            }
            return data
        except (ModbusError, KeyError, ValueError) as err:
            raise UpdateFailed(f"Unable to read MENNEKES registers: {err}") from err

    async def async_set_current_limit(self, value: int) -> None:
        """Set the HEMS current limit (register 1000)."""
        try:
            await self.client.write_single_register(1000, value)
        except ModbusError as err:
            raise UpdateFailed(f"Unable to set charging current: {err}") from err
        await self.async_request_refresh()

    async def async_set_availability(self, available: bool) -> None:
        """Set CP availability (register 124; firmware >= 5.22 semantics)."""
        try:
            await self.client.write_single_register(124, 1 if available else 0)
        except ModbusError as err:
            raise UpdateFailed(f"Unable to set availability: {err}") from err
        await self.async_request_refresh()


async def async_create_coordinator(hass: HomeAssistant, entry: ConfigEntry) -> MennekesCoordinator:
    """Create and perform the first coordinator refresh."""
    coordinator = MennekesCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        if isinstance(err, (UpdateFailed, TimeoutError, OSError, ModbusError)):
            raise ConfigEntryNotReady from err
        raise
    return coordinator

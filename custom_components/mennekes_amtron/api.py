"""Small dependency-free asynchronous Modbus TCP client.

The MENNEKES ECU exposes the documented registers as Modbus holding registers.
We intentionally implement only the Modbus TCP subset needed by the integration;
this avoids coupling the custom integration to a particular pymodbus version.
"""

from __future__ import annotations

import asyncio
import struct
from typing import Final

_LOG_PREFIX: Final = "MENNEKES Modbus TCP"


class ModbusError(Exception):
    """Base exception for Modbus communication errors."""


class ModbusConnectionError(ModbusError):
    """Connection or transport error."""


class ModbusResponseError(ModbusError):
    """Malformed or exception Modbus response."""


class MennekesModbusClient:
    """Minimal Modbus TCP client for the MENNEKES ECU register set."""

    def __init__(self, host: str, port: int = 502, timeout: float = 5) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self._transaction_id = 0

    def _next_transaction_id(self) -> int:
        self._transaction_id = (self._transaction_id + 1) & 0xFFFF
        return self._transaction_id

    async def _request(self, pdu: bytes, unit_id: int = 1) -> bytes:
        transaction_id = self._next_transaction_id()
        # MBAP length = unit-id byte + PDU length.
        header = struct.pack(">HHHB", transaction_id, 0, len(pdu) + 1, unit_id)
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port), self.timeout
            )
            writer.write(header + pdu)
            await writer.drain()
            response_header = await asyncio.wait_for(reader.readexactly(7), self.timeout)
            rx_tid, protocol_id, length, rx_unit = struct.unpack(">HHHB", response_header)
            if rx_tid != transaction_id or protocol_id != 0 or rx_unit != unit_id:
                raise ModbusResponseError("Invalid Modbus TCP response header")
            if length < 2:
                raise ModbusResponseError("Invalid Modbus TCP response length")
            response_pdu = await asyncio.wait_for(reader.readexactly(length - 1), self.timeout)
            if not response_pdu:
                raise ModbusResponseError("Empty Modbus response")
            if response_pdu[0] & 0x80:
                code = response_pdu[1] if len(response_pdu) > 1 else -1
                raise ModbusResponseError(f"Modbus exception response code {code}")
            return response_pdu
        except (asyncio.TimeoutError, OSError, asyncio.IncompleteReadError) as err:
            raise ModbusConnectionError(str(err) or "Connection failed") from err
        finally:
            if "writer" in locals():
                writer.close()
                try:
                    await writer.wait_closed()
                except OSError:
                    pass

    async def read_holding_registers(
        self, address: int, count: int, unit_id: int = 1
    ) -> list[int]:
        """Read holding registers using function code 0x03."""
        if not 0 <= address <= 0xFFFF or not 1 <= count <= 125:
            raise ValueError("Invalid Modbus register range")
        pdu = struct.pack(">BHH", 0x03, address, count)
        response = await self._request(pdu, unit_id)
        if len(response) < 2 or response[0] != 0x03:
            raise ModbusResponseError("Unexpected function code")
        byte_count = response[1]
        if byte_count != count * 2 or len(response) != byte_count + 2:
            raise ModbusResponseError("Invalid register response length")
        return list(struct.unpack(f">{count}H", response[2:]))

    async def write_single_register(
        self, address: int, value: int, unit_id: int = 1
    ) -> None:
        """Write one holding register using function code 0x06."""
        if not 0 <= address <= 0xFFFF or not 0 <= value <= 0xFFFF:
            raise ValueError("Invalid Modbus register/value")
        pdu = struct.pack(">BHH", 0x06, address, value)
        response = await self._request(pdu, unit_id)
        if response != pdu:
            raise ModbusResponseError("Modbus write response did not echo request")

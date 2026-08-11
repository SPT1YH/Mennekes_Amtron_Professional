"""Minimal asynchronous Modbus TCP client for MENNEKES ECU."""
from __future__ import annotations

import asyncio
import logging
import struct

_LOGGER = logging.getLogger(__name__)


class ModbusError(Exception):
    """Base Modbus error."""


class ModbusConnectionError(ModbusError):
    """TCP connection/transport error."""


class ModbusResponseError(ModbusError):
    """Invalid or exception Modbus response."""


class MennekesModbusClient:
    """Small Modbus TCP client using FC03 and FC06."""

    def __init__(
        self,
        host: str,
        port: int = 502,
        unit_id: int = 1,
        timeout: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self._transaction_id = 0

    def _next_tid(self) -> int:
        self._transaction_id = (self._transaction_id + 1) & 0xFFFF
        if self._transaction_id == 0:
            self._transaction_id = 1
        return self._transaction_id

    async def _request(self, pdu: bytes) -> bytes:
        tid = self._next_tid()
        mbap = struct.pack(">HHHB", tid, 0, len(pdu) + 1, self.unit_id)

        _LOGGER.debug(
            "TX %s:%s unit=%d tid=%d pdu=%s",
            self.host,
            self.port,
            self.unit_id,
            tid,
            pdu.hex(" "),
        )

        writer = None
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
            writer.write(mbap + pdu)
            await writer.drain()

            header = await asyncio.wait_for(
                reader.readexactly(7),
                timeout=self.timeout,
            )
            rx_tid, protocol_id, length, rx_unit = struct.unpack(">HHHB", header)

            if rx_tid != tid:
                raise ModbusResponseError(
                    f"Transaction ID mismatch: sent {tid}, received {rx_tid}"
                )
            if protocol_id != 0:
                raise ModbusResponseError(
                    f"Invalid Modbus protocol ID: {protocol_id}"
                )
            if rx_unit != self.unit_id:
                raise ModbusResponseError(
                    f"Unit ID mismatch: sent {self.unit_id}, received {rx_unit}"
                )
            if length < 2:
                raise ModbusResponseError(f"Invalid MBAP length: {length}")

            response_pdu = await asyncio.wait_for(
                reader.readexactly(length - 1),
                timeout=self.timeout,
            )

            _LOGGER.debug(
                "RX %s:%s unit=%d tid=%d pdu=%s",
                self.host,
                self.port,
                self.unit_id,
                rx_tid,
                response_pdu.hex(" "),
            )

            if response_pdu[0] & 0x80:
                code = response_pdu[1] if len(response_pdu) > 1 else -1
                raise ModbusResponseError(
                    f"Modbus exception response: function=0x{response_pdu[0]:02x}, "
                    f"exception={code}"
                )

            return response_pdu

        except ModbusError:
            raise
        except (asyncio.TimeoutError, OSError, asyncio.IncompleteReadError) as err:
            raise ModbusConnectionError(
                f"Modbus TCP communication failed: {err}"
            ) from err
        finally:
            if writer is not None:
                writer.close()
                try:
                    await writer.wait_closed()
                except OSError:
                    pass

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Read holding registers with FC03."""
        if not 0 <= address <= 0xFFFF:
            raise ValueError("Invalid register address")
        if not 1 <= count <= 125:
            raise ValueError("Invalid register count")

        pdu = struct.pack(">BHH", 0x03, address, count)
        response = await self._request(pdu)

        if len(response) < 2 or response[0] != 0x03:
            raise ModbusResponseError(
                f"Unexpected function code in response: 0x{response[0]:02x}"
            )

        byte_count = response[1]
        if byte_count != count * 2 or len(response) != byte_count + 2:
            raise ModbusResponseError(
                f"Invalid register payload: byte_count={byte_count}, "
                f"payload_len={len(response)}"
            )

        return list(struct.unpack(f">{count}H", response[2:]))

    async def write_single_register(self, address: int, value: int) -> None:
        """Write one holding register with FC06."""
        if not 0 <= address <= 0xFFFF:
            raise ValueError("Invalid register address")
        if not 0 <= value <= 0xFFFF:
            raise ValueError("Invalid register value")

        pdu = struct.pack(">BHH", 0x06, address, value)
        response = await self._request(pdu)

        if response != pdu:
            raise ModbusResponseError(
                f"FC06 echo mismatch: sent={pdu.hex()} received={response.hex()}"
            )

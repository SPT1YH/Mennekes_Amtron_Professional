"""Tests for register decoding helpers."""

from custom_components.mennekes_amtron.coordinator import _ascii_u32, _error_u32, _u32


def test_u32_big_endian() -> None:
    registers = {200: 0x0001, 201: 0x1F40}
    assert _u32(registers, 200) == 73536


def test_ascii_u32() -> None:
    registers = {100: 0x352E, 101: 0x3333}
    assert _ascii_u32(registers, 100, 1) == "5.33"


def test_error_u32_special_order() -> None:
    registers = {111: 0x4100, 112: 0x0000}
    assert _error_u32(registers, 111) == 0x41

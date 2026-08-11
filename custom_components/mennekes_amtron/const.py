"""Constants for the MENNEKES AMTRON integration."""

from homeassistant.const import Platform

DOMAIN = "mennekes_amtron"
NAME = "MENNEKES AMTRON"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_TIMEOUT = 5

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
]

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

MIN_CHARGING_CURRENT = 6
MAX_CHARGING_CURRENT = 32

STATUS_NAMES = {
    0: "Available",
    1: "Occupied",
    2: "Reserved",
    3: "Unavailable",
    4: "Faulted",
    5: "Preparing",
    6: "Charging",
    7: "Suspended EVSE",
    8: "Suspended EV",
    9: "Finishing",
}

VEHICLE_STATE_NAMES = {
    0: "Unknown",
    1: "A",
    2: "B",
    3: "C",
    4: "D",
    5: "E",
}

ERROR_NAMES = {
    0: "Residual current detected",
    1: "Vehicle signals error",
    2: "Vehicle diode check failed",
    3: "MCB type 2 triggered",
    4: "MCB Schuko triggered",
    5: "RCD triggered",
    6: "Contactor welded",
    7: "Backend disconnected",
    8: "Plug locking failed",
    9: "Locking without plug failed",
    10: "Actuator stuck",
    11: "Actuator detection failed",
    12: "Firmware update running",
    13: "Charge point tilted",
    14: "CP/PR wiring issue",
    15: "Type 2 overload",
    16: "Actuator unlocked while charging",
    17: "Charging prevented after tilt until reboot",
    18: "PIC24 error",
    19: "USB stick handling in progress",
    20: "Incorrect phase rotation",
    21: "No mains power",
}

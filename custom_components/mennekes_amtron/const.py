from homeassistant.const import Platform

DOMAIN = "mennekes_amtron"
NAME = "MENNEKES AMTRON Professional"

DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_TIMEOUT = 5
DEFAULT_UNIT_ID = 1

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
]

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

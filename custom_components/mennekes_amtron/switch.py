# custom_components/mennekes_amtron/switch.py
from homeassistant.components.switch import SwitchEntity
from .const import DOMAIN
from .coordinator import MennekesAmtronCoordinator

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MennekesReleaseSwitch(coordinator)])

class MennekesReleaseSwitch(SwitchEntity):
    def __init__(self, coordinator: MennekesAmtronCoordinator):
        self.coordinator = coordinator
        self._attr_name = "MENNEKES Ladefreigabe"
        self._attr_unique_id = f"{coordinator.host}_ladefreigabe_switch"

    @property
    def is_on(self):
        return False

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_turn_on(self, **kwargs):
        pass

    async def async_turn_off(self, **kwargs):
        pass

    async def async_added_to_hass(self):
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
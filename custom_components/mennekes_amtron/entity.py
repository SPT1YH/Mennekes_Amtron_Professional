"""Shared entities for MENNEKES AMTRON."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MennekesCoordinator


class MennekesEntity(CoordinatorEntity[MennekesCoordinator]):
    """Base entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: MennekesCoordinator, unique_suffix: str) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.config_entry.entry_id)},
            "name": "MENNEKES AMTRON Professional",
            "manufacturer": "MENNEKES",
            "model": coordinator.data.get("model") or "AMTRON Professional",
            "sw_version": coordinator.data.get("firmware"),
        }
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{unique_suffix}"

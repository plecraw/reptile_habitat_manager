"""Switch platform for Reptile Habitat Manager."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ReptileHabitatCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""
    coordinator: ReptileHabitatCoordinator = entry.runtime_data
    
    entities = []
    
    # Heat source manual control switches
    for i in range(len(coordinator.config["heat_sources"])):
        entities.append(HeatSourceManualSwitch(coordinator, entry, i))
    
    # Master switches
    entities.extend([
        AllHeatSourcesSwitch(coordinator, entry),
        AutomationSwitch(coordinator, entry),
    ])
    
    async_add_entities(entities)


class HeatSourceManualSwitch(CoordinatorEntity[ReptileHabitatCoordinator], SwitchEntity):
    """Manual control switch for individual heat sources."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
        heat_source_index: int,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._entry = entry
        self._heat_source_index = heat_source_index
        self._attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_heat_{self._heat_source_index}_manual"

    @property
    def name(self) -> str:
        """Return the name."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return f"{self.coordinator.reptile_name} {heat_data['name']} Manual Control"
        return f"{self.coordinator.reptile_name} Heat Source {self._heat_source_index} Manual"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                switch_entity = heat_data.get("switch_entity")
                if switch_entity:
                    switch_state = self.hass.states.get(switch_entity)
                    return switch_state and switch_state.state == STATE_ON
        return False

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:fire" if self.is_on else "mdi:fire-off"

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index, {})
        return {
            "controlled_entity": heat_data.get("switch_entity"),
            "current_temp": heat_data.get("current_temp"),
            "target_min": heat_data.get("target_min"),
            "target_max": heat_data.get("target_max"),
            "status": heat_data.get("status"),
            "automation_active": self.coordinator.data.get("automation_enabled", True),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the heat source."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                switch_entity = heat_data.get("switch_entity")
                if switch_entity:
                    await self.hass.services.async_call(
                        "switch", "turn_on", {"entity_id": switch_entity}
                    )
                    # Set manual override
                    self.coordinator.set_manual_override(self._heat_source_index, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the heat source."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                switch_entity = heat_data.get("switch_entity")
                if switch

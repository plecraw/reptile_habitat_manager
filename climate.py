"""Climate platform for Reptile Habitat Manager."""
from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
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
    """Set up climate entities."""
    coordinator: ReptileHabitatCoordinator = entry.runtime_data
    
    entities = []
    
    # Create climate entity for each heat source
    for i in range(len(coordinator.config["heat_sources"])):
        entities.append(HeatSourceClimate(coordinator, entry, i))
    
    # Add tank atmosphere climate
    entities.append(AtmosphereClimate(coordinator, entry))
    
    async_add_entities(entities)


class HeatSourceClimate(CoordinatorEntity[ReptileHabitatCoordinator], ClimateEntity):
    """Climate entity for individual heat sources."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
        heat_source_index: int,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._heat_source_index = heat_source_index
        self._attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_heat_{self._heat_source_index}"

    @property
    def name(self) -> str:
        """Return the name."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return f"{self.coordinator.reptile_name} {heat_data['name']}"
        return f"{self.coordinator.reptile_name} Heat Source {self._heat_source_index}"

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.FAHRENHEIT

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return heat_data.get("current_temp")
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                target_min = heat_data.get("target_min", 75)
                target_max = heat_data.get("target_max", 85)
                return (target_min + target_max) / 2
        return None

    @property
    def target_temperature_high(self) -> float | None:
        """Return the high target temperature."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return heat_data.get("target_max")
        return None

    @property
    def target_temperature_low(self) -> float | None:
        """Return the low target temperature."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return heat_data.get("target_min")
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        return HVACMode.HEAT

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return available HVAC modes."""
        return [HVACMode.HEAT]

    @property
    def hvac_action(self) -> HVACAction:
        """Return current HVAC action."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data and heat_data.get("is_heating"):
                return HVACAction.HEATING
            return HVACAction.IDLE
        return HVACAction.OFF

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE_RANGE

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index, {})
        return {
            "critical_min": heat_data.get("critical_min"),
            "critical_max": heat_data.get("critical_max"),
            "status": heat_data.get("status"),
            "switch_entity": heat_data.get("switch_entity"),
            "sensor_entity": heat_data.get("sensor_entity"),
        }


class AtmosphereClimate(CoordinatorEntity[ReptileHabitatCoordinator], ClimateEntity):
    """Climate entity for tank atmosphere."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the atmosphere climate entity."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_atmosphere"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Tank Atmosphere"

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.FAHRENHEIT

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if self.coordinator.data:
            atmosphere_data = self.coordinator.data.get("atmosphere", {})
            return atmosphere_data.get("current_temp")
        return None

    @property
    def current_humidity(self) -> float | None:
        """Return the current humidity."""
        if self.coordinator.data:
            atmosphere_data = self.coordinator.data.get("atmosphere", {})
            return atmosphere_data.get("current_humidity")
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        if self.coordinator.data:
            atmosphere_data = self.coordinator.data.get("atmosphere", {})
            target_min = atmosphere_data.get("target_min_temp", 75)
            target_max = atmosphere_data.get("target_max_temp", 85)
            return (target_min + target_max) / 2
        return None

    @property
    def target_temperature_high(self) -> float | None:
        """Return the high target temperature."""
        if self.coordinator.data:
            atmosphere_data = self.coordinator.data.get("atmosphere", {})
            return atmosphere_data.get("target_max_temp")
        return None

    @property
    def target_temperature_low(self) -> float | None:
        """Return the low target temperature."""
        if self.coordinator.data:
            atmosphere_data = self.coordinator.data.get("atmosphere", {})
            return atmosphere_data.get("target_min_temp")
        return None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        return HVACMode.AUTO

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return available HVAC modes."""
        return [HVACMode.AUTO]

    @property
    def hvac_action(self) -> HVACAction:
        """Return current HVAC action."""
        return HVACAction.IDLE

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE_RANGE

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        atmosphere_data = self.coordinator.data.get("atmosphere", {})
        return {
            "current_humidity": atmosphere_data.get("current_humidity"),
            "target_min_humidity": atmosphere_data.get("target_min_humidity"),
            "target_max_humidity": atmosphere_data.get("target_max_humidity"),
            "critical_min_humidity": atmosphere_data.get("critical_min_humidity"),
            "critical_max_humidity": atmosphere_data.get("critical_max_humidity"),
            "critical_min_temp": atmosphere_data.get("critical_min_temp"),
            "critical_max_temp": atmosphere_data.get("critical_max_temp"),
            "temp_sensor": atmosphere_data.get("temp_sensor"),
            "humidity_sensor": atmosphere_data.get("humidity_sensor"),
        }

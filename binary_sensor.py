"""Binary sensor platform for Reptile Habitat Manager."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
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
    """Set up binary sensor entities."""
    coordinator: ReptileHabitatCoordinator = entry.runtime_data
    
    entities = []
    
    # Heat source binary sensors
    for i in range(len(coordinator.config["heat_sources"])):
        entities.extend([
            HeatSourceProblemSensor(coordinator, entry, i),
            HeatSourceActiveSensor(coordinator, entry, i),
        ])
    
    # General binary sensors
    entities.extend([
        AtmosphereProblemSensor(coordinator, entry),
        OverallHealthSensor(coordinator, entry),
        FeedingOverdueSensor(coordinator, entry),
        WeightLossSensor(coordinator, entry),
    ])
    
    async_add_entities(entities)


class HeatSourceProblemSensor(CoordinatorEntity[ReptileHabitatCoordinator], BinarySensorEntity):
    """Binary sensor for heat source problems."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
        heat_source_index: int,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._heat_source_index = heat_source_index
        self._attr_has_entity_name = True
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_heat_{self._heat_source_index}_problem"

    @property
    def name(self) -> str:
        """Return the name."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return f"{self.coordinator.reptile_name} {heat_data['name']} Problem"
        return f"{self.coordinator.reptile_name} Heat Source {self._heat_source_index} Problem"

    @property
    def is_on(self) -> bool:
        """Return true if there's a problem."""
        if not self.coordinator.data:
            return False
            
        heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index, {})
        status = heat_data.get("status", "unknown")
        return status.startswith("critical") or status == "unknown"

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index, {})
        return {
            "status": heat_data.get("status"),
            "current_temp": heat_data.get("current_temp"),
            "target_min": heat_data.get("target_min"),
            "target_max": heat_data.get("target_max"),
        }


class HeatSourceActiveSensor(CoordinatorEntity[ReptileHabitatCoordinator], BinarySensorEntity):
    """Binary sensor for heat source activity."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
        heat_source_index: int,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._heat_source_index = heat_source_index
        self._attr_has_entity_name = True
        self._attr_device_class = BinarySensorDeviceClass.HEAT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_heat_{self._heat_source_index}_active"

    @property
    def name(self) -> str:
        """Return the name."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return f"{self.coordinator.reptile_name} {heat_data['name']} Active"
        return f"{self.coordinator.reptile_name} Heat Source {self._heat_source_index} Active"

    @property
    def is_on(self) -> bool:
        """Return true if heat source is active."""
        if not self.coordinator.data:
            return False
            
        heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index, {})
        return heat_data.get("is_heating", False)

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:fire" if self.is_on else "mdi:fire-off"


class AtmosphereProblemSensor(CoordinatorEntity[ReptileHabitatCoordinator], BinarySensorEntity):
    """Binary sensor for atmosphere problems."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_atmosphere_problem"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Atmosphere Problem"

    @property
    def is_on(self) -> bool:
        """Return true if there's an atmosphere problem."""
        if not self.coordinator.data:
            return False
            
        atmosphere_data = self.coordinator.data.get("atmosphere", {})
        
        # Check temperature
        current_temp = atmosphere_data.get("current_temp")
        if current_temp is not None:
            critical_min_temp = atmosphere_data.get("critical_min_temp", 0)
            critical_max_temp = atmosphere_data.get("critical_max_temp", 150)
            if current_temp <= critical_min_temp or current_temp >= critical_max_temp:
                return True
        
        # Check humidity
        current_humidity = atmosphere_data.get("current_humidity")
        if current_humidity is not None:
            critical_min_humidity = atmosphere_data.get("critical_min_humidity", 0)
            critical_max_humidity = atmosphere_data.get("critical_max_humidity", 100)
            if current_humidity <= critical_min_humidity or current_humidity >= critical_max_humidity:
                return True
        
        return False

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        atmosphere_data = self.coordinator.data.get("atmosphere", {})
        return {
            "current_temp": atmosphere_data.get("current_temp"),
            "current_humidity": atmosphere_data.get("current_humidity"),
            "critical_min_temp": atmosphere_data.get("critical_min_temp"),
            "critical_max_temp": atmosphere_data.get("critical_max_temp"),
            "critical_min_humidity": atmosphere_data.get("critical_min_humidity"),
            "critical_max_humidity": atmosphere_data.get("critical_max_humidity"),
        }


class OverallHealthSensor(CoordinatorEntity[ReptileHabitatCoordinator], BinarySensorEntity):
    """Binary sensor for overall habitat health."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_device_class = BinarySensorDeviceClass.SAFETY

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_overall_health"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Habitat Healthy"

    @property
    def is_on(self) -> bool:
        """Return true if habitat is healthy."""
        if not self.coordinator.data:
            return False
            
        # Check heat sources
        heat_sources = self.coordinator.data.get("heat_sources", {})
        for heat_data in heat_sources.values():
            if heat_data.get("status", "").startswith("critical"):
                return False
        
        # Check atmosphere
        atmosphere_data = self.coordinator.data.get("atmosphere", {})
        current_temp = atmosphere_data.get("current_temp")
        if current_temp is not None:
            critical_min_temp = atmosphere_data.get("critical_min_temp", 0)
            critical_max_temp = atmosphere_data.get("critical_max_temp", 150)
            if current_temp <= critical_min_temp or current_temp >= critical_max_temp:
                return False
        
        current_humidity = atmosphere_data.get("current_humidity")
        if current_humidity is not None:
            critical_min_humidity = atmosphere_data.get("critical_min_humidity", 0)
            critical_max_humidity = atmosphere_data.get("critical_max_humidity", 100)
            if current_humidity <= critical_min_humidity or current_humidity >= critical_max_humidity:
                return False
        
        return True

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:check-circle" if self.is_on else "mdi:alert-circle"


class FeedingOverdueSensor(CoordinatorEntity[ReptileHabitatCoordinator], BinarySensorEntity):
    """Binary sensor for overdue feeding."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_feeding_overdue"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Feeding Overdue"

    @property
    def is_on(self) -> bool:
        """Return true if feeding is overdue."""
        if not self.coordinator.data:
            return False
            
        feeding_log = self.coordinator.data["care"]["feeding_log"]
        if not feeding_log:
            return True  # No feeding recorded = overdue
            
        last_feeding = feeding_log[-1]
        days_since = (datetime.now() - last_feeding["date"]).days
        
        # Consider feeding overdue after 14 days (adjust as needed)
        return days_since > 14

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:food-off" if self.is_on else "mdi:food"

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        feeding_log = self.coordinator.data["care"]["feeding_log"]
        if feeding_log:
            last_feeding = feeding_log[-1]
            days_since = (datetime.now() - last_feeding["date"]).days
            return {
                "days_since_feeding": days_since,
                "last_food_type": last_feeding.get("food_type"),
                "feeding_threshold_days": 14,
            }
        return {"days_since_feeding": "unknown", "feeding_threshold_days": 14}


class WeightLossSensor(CoordinatorEntity[ReptileHabitatCoordinator], BinarySensorEntity):
    """Binary sensor for significant weight loss."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_weight_loss"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Significant Weight Loss"

    @property
    def is_on(self) -> bool:
        """Return true if there's significant weight loss."""
        if not self.coordinator.data:
            return False
            
        weight_log = self.coordinator.data["care"]["weight_log"]
        if len(weight_log) < 2:
            return False
            
        current_weight = weight_log[-1]["weight"]
        previous_weight = weight_log[-2]["weight"]
        
        # Consider >10% weight loss as significant
        weight_loss_percent = ((previous_weight - current_weight) / previous_weight) * 100
        return weight_loss_percent > 10

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:trending-down" if self.is_on else "mdi:scale"

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        weight_log = self.coordinator.data["care"]["weight_log"]
        if len(weight_log) >= 2:
            current_weight = weight_log[-1]["weight"]
            previous_weight = weight_log[-2]["weight"]
            weight_change = current_weight - previous_weight
            weight_loss_percent = ((previous_weight - current_weight) / previous_weight) * 100
            
            return {
                "current_weight": current_weight,
                "previous_weight": previous_weight,
                "weight_change": round(weight_change, 1),
                "weight_loss_percent": round(weight_loss_percent, 1),
                "weight_loss_threshold": 10,
            }
        return {}

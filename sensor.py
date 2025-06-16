"""Sensor platform for Reptile Habitat Manager."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfMass, UnitOfTemperature
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
    """Set up sensor entities."""
    coordinator: ReptileHabitatCoordinator = entry.runtime_data
    
    entities = []
    
    # Heat source sensors
    for i in range(len(coordinator.config["heat_sources"])):
        entities.extend([
            HeatSourceTemperatureSensor(coordinator, entry, i),
            HeatSourceStatusSensor(coordinator, entry, i),
        ])
    
    # Atmosphere sensors
    entities.extend([
        AtmosphereTemperatureSensor(coordinator, entry),
        AtmosphereHumiditySensor(coordinator, entry),
        TankStatusSensor(coordinator, entry),
    ])
    
    # Care tracking sensors
    entities.extend([
        LastFeedingSensor(coordinator, entry),
        LastSheddingSensor(coordinator, entry),
        CurrentWeightSensor(coordinator, entry),
        FeedingCountSensor(coordinator, entry),
        WeightTrendSensor(coordinator, entry),
    ])
    
    async_add_entities(entities)


class HeatSourceTemperatureSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Temperature sensor for heat sources."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
        heat_source_index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._heat_source_index = heat_source_index
        self._attr_has_entity_name = True
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_heat_{self._heat_source_index}_temp"

    @property
    def name(self) -> str:
        """Return the name."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return f"{self.coordinator.reptile_name} {heat_data['name']} Temperature"
        return f"{self.coordinator.reptile_name} Heat Source {self._heat_source_index} Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return heat_data.get("current_temp")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index, {})
        return {
            "target_min": heat_data.get("target_min"),
            "target_max": heat_data.get("target_max"),
            "critical_min": heat_data.get("critical_min"),
            "critical_max": heat_data.get("critical_max"),
            "status": heat_data.get("status"),
            "is_heating": heat_data.get("is_heating"),
        }


class HeatSourceStatusSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Status sensor for heat sources."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
        heat_source_index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._heat_source_index = heat_source_index
        self._attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_heat_{self._heat_source_index}_status"

    @property
    def name(self) -> str:
        """Return the name."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return f"{self.coordinator.reptile_name} {heat_data['name']} Status"
        return f"{self.coordinator.reptile_name} Heat Source {self._heat_source_index} Status"

    @property
    def native_value(self) -> str:
        """Return the state."""
        if self.coordinator.data:
            heat_data = self.coordinator.data["heat_sources"].get(self._heat_source_index)
            if heat_data:
                return heat_data.get("status", "unknown")
        return "unknown"

    @property
    def icon(self) -> str:
        """Return the icon."""
        status = self.native_value
        if status == "critical_low":
            return "mdi:thermometer-low"
        elif status == "critical_high":
            return "mdi:thermometer-high"
        elif status == "heating":
            return "mdi:fire"
        elif status == "ok":
            return "mdi:check-circle"
        return "mdi:thermometer"


class AtmosphereTemperatureSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Tank atmosphere temperature sensor."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_atmosphere_temp"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Tank Temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        if self.coordinator.data:
            atmosphere_data = self.coordinator.data.get("atmosphere", {})
            return atmosphere_data.get("current_temp")
        return None


class AtmosphereHumiditySensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Tank atmosphere humidity sensor."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_device_class = SensorDeviceClass.HUMIDITY
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_atmosphere_humidity"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Tank Humidity"

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        if self.coordinator.data:
            atmosphere_data = self.coordinator.data.get("atmosphere", {})
            return atmosphere_data.get("current_humidity")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        atmosphere_data = self.coordinator.data.get("atmosphere", {})
        return {
            "target_min": atmosphere_data.get("target_min_humidity"),
            "target_max": atmosphere_data.get("target_max_humidity"),
            "critical_min": atmosphere_data.get("critical_min_humidity"),
            "critical_max": atmosphere_data.get("critical_max_humidity"),
        }


class TankStatusSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Overall tank status sensor."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_tank_status"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Tank Status"

    @property
    def native_value(self) -> str:
        """Return the state."""
        if not self.coordinator.data:
            return "unknown"
            
        # Check heat sources for critical status
        heat_sources = self.coordinator.data.get("heat_sources", {})
        for heat_data in heat_sources.values():
            if heat_data.get("status", "").startswith("critical"):
                return "critical"
        
        return "ok"

    @property
    def icon(self) -> str:
        """Return the icon."""
        status = self.native_value
        if status == "critical":
            return "mdi:alert-circle"
        elif status == "ok":
            return "mdi:check-circle"
        return "mdi:help-circle"


class LastFeedingSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Last feeding date sensor."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_last_feeding"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Last Feeding"

    @property
    def native_value(self) -> datetime | None:
        """Return the state."""
        if self.coordinator.data:
            feeding_log = self.coordinator.data["care"]["feeding_log"]
            if feeding_log:
                return feeding_log[-1]["date"]
        return None

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
                "food_type": last_feeding.get("food_type"),
                "food_size": last_feeding.get("food_size"),
                "notes": last_feeding.get("notes"),
                "days_since_feeding": days_since,
            }
        return {}


class LastSheddingSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Last shedding date sensor."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_last_shedding"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Last Shedding"

    @property
    def native_value(self) -> datetime | None:
        """Return the state."""
        if self.coordinator.data:
            shedding_log = self.coordinator.data["care"]["shedding_log"]
            if shedding_log:
                return shedding_log[-1]["date"]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        shedding_log = self.coordinator.data["care"]["shedding_log"]
        if shedding_log:
            last_shedding = shedding_log[-1]
            days_since = (datetime.now() - last_shedding["date"]).days
            return {
                "complete": last_shedding.get("complete"),
                "notes": last_shedding.get("notes"),
                "days_since_shedding": days_since,
            }
        return {}


class CurrentWeightSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Current weight sensor."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_current_weight"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Current Weight"

    @property
    def native_value(self) -> float | None:
        """Return the state."""
        if self.coordinator.data:
            weight_log = self.coordinator.data["care"]["weight_log"]
            if weight_log:
                return weight_log[-1]["weight"]
        return None

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        if self.coordinator.data:
            weight_log = self.coordinator.data["care"]["weight_log"]
            if weight_log:
                unit = weight_log[-1].get("unit", "g")
                if unit == "g":
                    return UnitOfMass.GRAMS
                elif unit == "kg":
                    return UnitOfMass.KILOGRAMS
                elif unit == "oz":
                    return UnitOfMass.OUNCES
                elif unit == "lb":
                    return UnitOfMass.POUNDS
        return UnitOfMass.GRAMS

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        weight_log = self.coordinator.data["care"]["weight_log"]
        if weight_log:
            last_weight = weight_log[-1]
            days_since = (datetime.now() - last_weight["date"]).days
            return {
                "weight_date": last_weight["date"].isoformat(),
                "notes": last_weight.get("notes"),
                "days_since_weigh": days_since,
            }
        return {}


class FeedingCountSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Monthly feeding count sensor."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True
        self._attr_state_class = SensorStateClass.TOTAL
        self._attr_icon = "mdi:food"

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_feeding_count_month"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Feedings This Month"

    @property
    def native_value(self) -> int:
        """Return the state."""
        if not self.coordinator.data:
            return 0
            
        feeding_log = self.coordinator.data["care"]["feeding_log"]
        now = datetime.now()
        current_month_feedings = [
            feeding for feeding in feeding_log
            if feeding["date"].year == now.year and feeding["date"].month == now.month
        ]
        return len(current_month_feedings)


class WeightTrendSensor(CoordinatorEntity[ReptileHabitatCoordinator], SensorEntity):
    """Weight trend sensor."""

    def __init__(
        self,
        coordinator: ReptileHabitatCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_has_entity_name = True

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return f"{self._entry.entry_id}_weight_trend"

    @property
    def name(self) -> str:
        """Return the name."""
        return f"{self.coordinator.reptile_name} Weight Trend"

    @property
    def native_value(self) -> str:
        """Return the state."""
        if not self.coordinator.data:
            return "unknown"
            
        weight_log = self.coordinator.data["care"]["weight_log"]
        if len(weight_log) < 2:
            return "insufficient_data"
            
        current_weight = weight_log[-1]["weight"]
        previous_weight = weight_log[-2]["weight"]
        
        if current_weight > previous_weight * 1.02:  # 2% increase
            return "increasing"
        elif current_weight < previous_weight * 0.98:  # 2% decrease
            return "decreasing"
        else:
            return "stable"

    @property
    def icon(self) -> str:
        """Return the icon."""
        trend = self.native_value
        if trend == "increasing":
            return "mdi:trending-up"
        elif trend == "decreasing":
            return "mdi:trending-down"
        elif trend == "stable":
            return "mdi:trending-neutral"
        return "mdi:help-circle"

    @property
    def extra_state_attributes(self) -> dict[str, any]:
        """Return extra state attributes."""
        if not self.coordinator.data:
            return {}
            
        weight_log = self.coordinator.data["care"]["weight_log"]
        if len(weight_log) >= 2:
            current_weight = weight_log[-1]["weight"]
            previous_weight = weight_log[-2]["weight"]
            change = current_weight - previous_weight
            change_percent = (change / previous_weight) * 100
            
            return {
                "current_weight": current_weight,
                "previous_weight": previous_weight,
                "weight_change": round(change, 1),
                "weight_change_percent": round(change_percent, 1),
                "total_measurements": len(weight_log),
            }
        return {}

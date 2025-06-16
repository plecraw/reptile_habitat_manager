"""Data coordinator for Reptile Habitat Manager."""
import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.const import STATE_ON, STATE_OFF

from .const import (
    DOMAIN,
    DEFAULT_UPDATE_INTERVAL,
    CONF_REPTILE_NAME,
    CONF_HEAT_SOURCES,
    CONF_HEAT_NAME,
    CONF_HEAT_SWITCH,
    CONF_HEAT_SENSOR,
    CONF_TARGET_MIN,
    CONF_TARGET_MAX,
    CONF_CRITICAL_MIN,
    CONF_CRITICAL_MAX,
    CONF_ATMO_TEMP_SENSOR,
    CONF_ATMO_HUMIDITY_SENSOR,
    CONF_ATMO_TARGET_MIN_TEMP,
    CONF_ATMO_TARGET_MAX_TEMP,
    CONF_ATMO_CRITICAL_MIN_TEMP,
    CONF_ATMO_CRITICAL_MAX_TEMP,
    CONF_ATMO_TARGET_MIN_HUMIDITY,
    CONF_ATMO_TARGET_MAX_HUMIDITY,
    CONF_ATMO_CRITICAL_MIN_HUMIDITY,
    CONF_ATMO_CRITICAL_MAX_HUMIDITY,
    STATUS_OK,
    STATUS_HEATING,
    STATUS_COOLING,
    STATUS_CRITICAL_LOW,
    STATUS_CRITICAL_HIGH,
    STATUS_BELOW_TARGET,
    STATUS_ABOVE_TARGET,
    STATUS_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)


class ReptileHabitatCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Reptile Habitat data."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize."""
        self.entry = entry
        self.config = entry.data
        self._automation_enabled = True
        self._manual_overrides = {}
        self._last_notifications = {}
        
        # Care tracking
        self._feeding_log = []
        self._shedding_log = []
        self._weight_log = []
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )

    @property
    def reptile_name(self) -> str:
        """Return reptile name."""
        return self.config[CONF_REPTILE_NAME]

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from sensors and control heating."""
        try:
            data = {
                "reptile_name": self.reptile_name,
                "heat_sources": {},
                "atmosphere": {},
                "care": {
                    "feeding_log": self._feeding_log,
                    "shedding_log": self._shedding_log,
                    "weight_log": self._weight_log,
                },
                "automation_enabled": self._automation_enabled,
                "last_update": datetime.now(),
            }

            # Process heat sources
            for i, heat_config in enumerate(self.config[CONF_HEAT_SOURCES]):
                data["heat_sources"][i] = await self._process_heat_source(heat_config, i)

            # Process atmosphere
            data["atmosphere"] = await self._process_atmosphere()

            return data

        except Exception as err:
            raise UpdateFailed(f"Error updating data: {err}")

    async def _process_heat_source(self, config: dict, index: int) -> dict[str, Any]:
        """Process individual heat source."""
        # Get sensor states
        temp_state = self.hass.states.get(config[CONF_HEAT_SENSOR])
        switch_state = self.hass.states.get(config[CONF_HEAT_SWITCH])
        
        current_temp = None
        if temp_state and temp_state.state not in ["unknown", "unavailable"]:
            try:
                current_temp = float(temp_state.state)
            except (ValueError, TypeError):
                current_temp = None
        
        is_heating = switch_state and switch_state.state == STATE_ON
        
        heat_data = {
            "name": config[CONF_HEAT_NAME],
            "current_temp": current_temp,
            "target_min": config[CONF_TARGET_MIN],
            "target_max": config[CONF_TARGET_MAX],
            "critical_min": config[CONF_CRITICAL_MIN],
            "critical_max": config[CONF_CRITICAL_MAX],
            "switch_entity": config[CONF_HEAT_SWITCH],
            "sensor_entity": config[CONF_HEAT_SENSOR],
            "is_heating": is_heating,
            "status": STATUS_UNKNOWN,
            "alerts": [],
        }

        if current_temp is not None:
            # Determine status and control heating
            await self._control_heat_source(heat_data, config, index, current_temp)
        
        return heat_data

    async def _control_heat_source(self, heat_data: dict, config: dict, index: int, temp: float):
        """Control individual heat source based on temperature."""
        # Check for critical conditions first
        if temp <= config[CONF_CRITICAL_MIN]:
            heat_data["status"] = STATUS_CRITICAL_LOW
            await self._send_alert(f"CRITICAL: {config[CONF_HEAT_NAME]} too cold: {temp}°F")
            return
        
        if temp >= config[CONF_CRITICAL_MAX]:
            heat_data["status"] = STATUS_CRITICAL_HIGH
            await self._send_alert(f"CRITICAL: {config[CONF_HEAT_NAME]} too hot: {temp}°F")
            return

        # Only control if automation enabled and no manual override
        if not self._automation_enabled or self._manual_overrides.get(index, False):
            heat_data["status"] = STATUS_OK if self._automation_enabled else "manual"
            return

        # Normal temperature control
        is_heating = heat_data["is_heating"]
        
        if temp < config[CONF_TARGET_MIN] and not is_heating:
            # Turn on heating
            await self.hass.services.async_call(
                "switch", "turn_on", {"entity_id": config[CONF_HEAT_SWITCH]}
            )
            heat_data["status"] = STATUS_HEATING
        elif temp > config[CONF_TARGET_MAX] and is_heating:
            # Turn off heating
            await self.hass.services.async_call(
                "switch", "turn_off", {"entity_id": config[CONF_HEAT_SWITCH]}
            )
            heat_data["status"] = STATUS_COOLING
        elif temp < config[CONF_TARGET_MIN]:
            heat_data["status"] = STATUS_BELOW_TARGET
        elif temp > config[CONF_TARGET_MAX]:
            heat_data["status"] = STATUS_ABOVE_TARGET
        else:
            heat_data["status"] = STATUS_OK

    async def _process_atmosphere(self) -> dict[str, Any]:
        """Process tank atmosphere data."""
        temp_state = self.hass.states.get(self.config[CONF_ATMO_TEMP_SENSOR])
        humidity_state = self.hass.states.get(self.config[CONF_ATMO_HUMIDITY_SENSOR])
        
        current_temp = None
        current_humidity = None
        
        if temp_state and temp_state.state not in ["unknown", "unavailable"]:
            try:
                current_temp = float(temp_state.state)
            except (ValueError, TypeError):
                pass
        
        if humidity_state and humidity_state.state not in ["unknown", "unavailable"]:
            try:
                current_humidity = float(humidity_state.state)
            except (ValueError, TypeError):
                pass

        atmosphere_data = {
            "current_temp": current_temp,
            "current_humidity": current_humidity,
            "temp_sensor": self.config[CONF_ATMO_TEMP_SENSOR],
            "humidity_sensor": self.config[CONF_ATMO_HUMIDITY_SENSOR],
            "target_min_temp": self.config[CONF_ATMO_TARGET_MIN_TEMP],
            "target_max_temp": self.config[CONF_ATMO_TARGET_MAX_TEMP],
            "critical_min_temp": self.config[CONF_ATMO_CRITICAL_MIN_TEMP],
            "critical_max_temp": self.config[CONF_ATMO_CRITICAL_MAX_TEMP],
            "target_min_humidity": self.config[CONF_ATMO_TARGET_MIN_HUMIDITY],
            "target_max_humidity": self.config[CONF_ATMO_TARGET_MAX_HUMIDITY],
            "critical_min_humidity": self.config[CONF_ATMO_CRITICAL_MIN_HUMIDITY],
            "critical_max_humidity": self.config[CONF_ATMO_CRITICAL_MAX_HUMIDITY],
            "alerts": [],
        }

        # Check for critical conditions
        if current_temp is not None:
            if current_temp <= self.config[CONF_ATMO_CRITICAL_MIN_TEMP]:
                await self._send_alert(f"CRITICAL: Tank temperature too low: {current_temp}°F")
            elif current_temp >= self.config[CONF_ATMO_CRITICAL_MAX_TEMP]:
                await self._send_alert(f"CRITICAL: Tank temperature too high: {current_temp}°F")

        if current_humidity is not None:
            if current_humidity <= self.config[CONF_ATMO_CRITICAL_MIN_HUMIDITY]:
                await self._send_alert(f"CRITICAL: Tank humidity too low: {current_humidity}%")
            elif current_humidity >= self.config[CONF_ATMO_CRITICAL_MAX_HUMIDITY]:
                await self._send_alert(f"CRITICAL: Tank humidity too high: {current_humidity}%")

        return atmosphere_data

    async def _send_alert(self, message: str):
        """Send alert notification with cooldown."""
        alert_id = message[:50]  # Use first 50 chars as ID
        now = datetime.now()
        
        # Check cooldown
        if alert_id in self._last_notifications:
            last_sent = self._last_notifications[alert_id]
            if now - last_sent < timedelta(minutes=30):
                return
        
        self._last_notifications[alert_id] = now
        
        # Try to send mobile notification
        try:
            await self.hass.services.async_call(
                "notify",
                "mobile_app_phone",
                {
                    "title": f"🐍 {self.reptile_name} Alert",
                    "message": message,
                    "data": {"priority": "high", "color": "red"},
                }
            )
        except Exception as e:
            _LOGGER.warning("Failed to send mobile notification: %s", e)

    def set_automation_enabled(self, enabled: bool):
        """Enable/disable automation."""
        self._automation_enabled = enabled
        if enabled:
            self._manual_overrides.clear()

    def set_manual_override(self, heat_source_index: int, override: bool):
        """Set manual override for heat source."""
        self._manual_overrides[heat_source_index] = override

    async def log_feeding(self, food_type: str, food_size: str, notes: str = ""):
        """Log a feeding event."""
        entry = {
            "date": datetime.now(),
            "food_type": food_type,
            "food_size": food_size,
            "notes": notes,
        }
        self._feeding_log.append(entry)
        # Keep only last 50 entries
        self._feeding_log = self._feeding_log[-50:]
        await self.async_request_refresh()

    async def log_shedding(self, complete: bool, notes: str = ""):
        """Log a shedding event."""
        entry = {
            "date": datetime.now(),
            "complete": complete,
            "notes": notes,
        }
        self._shedding_log.append(entry)
        self._shedding_log = self._shedding_log[-20:]
        await self.async_request_refresh()

    async def log_weight(self, weight: float, unit: str = "g", notes: str = ""):
        """Log a weight measurement."""
        entry = {
            "date": datetime.now(),
            "weight": weight,
            "unit": unit,
            "notes": notes,
        }
        self._weight_log.append(entry)
        self._weight_log = self._weight_log[-50:]
        await self.async_request_refresh()

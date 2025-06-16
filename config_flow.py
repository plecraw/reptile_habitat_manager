"""Config flow for Reptile Habitat Manager integration."""
import logging

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
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
)

_LOGGER = logging.getLogger(__name__)


class ReptileHabitatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Reptile Habitat Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step - create entry with test data."""
        
        # For now, just create a test entry immediately
        return self.async_create_entry(
            title="Reptile Habitat - Test Snake",
            data={
                CONF_REPTILE_NAME: "Test Snake",
                CONF_HEAT_SOURCES: [
                    {
                        CONF_HEAT_NAME: "Basking Spot",
                        CONF_HEAT_SWITCH: "switch.test_basking_heater",
                        CONF_HEAT_SENSOR: "sensor.test_basking_temp",
                        CONF_TARGET_MIN: 85.0,
                        CONF_TARGET_MAX: 95.0,
                        CONF_CRITICAL_MIN: 75.0,
                        CONF_CRITICAL_MAX: 105.0,
                    },
                    {
                        CONF_HEAT_NAME: "Heat Mat",
                        CONF_HEAT_SWITCH: "switch.test_heat_mat",
                        CONF_HEAT_SENSOR: "sensor.test_mat_temp", 
                        CONF_TARGET_MIN: 80.0,
                        CONF_TARGET_MAX: 88.0,
                        CONF_CRITICAL_MIN: 70.0,
                        CONF_CRITICAL_MAX: 95.0,
                    },
                ],
                CONF_ATMO_TEMP_SENSOR: "sensor.test_tank_temp",
                CONF_ATMO_HUMIDITY_SENSOR: "sensor.test_tank_humidity",
                CONF_ATMO_TARGET_MIN_TEMP: 75.0,
                CONF_ATMO_TARGET_MAX_TEMP: 85.0,
                CONF_ATMO_CRITICAL_MIN_TEMP: 65.0,
                CONF_ATMO_CRITICAL_MAX_TEMP: 95.0,
                CONF_ATMO_TARGET_MIN_HUMIDITY: 50.0,
                CONF_ATMO_TARGET_MAX_HUMIDITY: 70.0,
                CONF_ATMO_CRITICAL_MIN_HUMIDITY: 30.0,
                CONF_ATMO_CRITICAL_MAX_HUMIDITY: 90.0,
            }
        )

"""The Reptile Habitat Manager integration."""
import logging
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_LOG_FEEDING,
    SERVICE_LOG_SHEDDING,
    SERVICE_LOG_WEIGHT,
)
from .coordinator import ReptileHabitatCoordinator

_LOGGER = logging.getLogger(__name__)

type ReptileHabitatConfigEntry = ConfigEntry[ReptileHabitatCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ReptileHabitatConfigEntry) -> bool:
    """Set up Reptile Habitat from a config entry."""
    coordinator = ReptileHabitatCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    entry.runtime_data = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Setup services
    await _async_setup_services(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ReptileHabitatConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up services."""
    
    async def log_feeding(call):
        """Log feeding service."""
        food_type = call.data.get("food_type")
        food_size = call.data.get("food_size") 
        notes = call.data.get("notes", "")
        
        # Find coordinator from any reptile habitat entry
        for entry in hass.config_entries.async_entries(DOMAIN):
            coordinator = entry.runtime_data
            await coordinator.log_feeding(food_type, food_size, notes)
            break
    
    async def log_shedding(call):
        """Log shedding service."""
        complete = call.data.get("complete")
        notes = call.data.get("notes", "")
        
        for entry in hass.config_entries.async_entries(DOMAIN):
            coordinator = entry.runtime_data
            await coordinator.log_shedding(complete, notes)
            break
    
    async def log_weight(call):
        """Log weight service."""
        weight = call.data.get("weight")
        unit = call.data.get("unit", "g")
        notes = call.data.get("notes", "")
        
        for entry in hass.config_entries.async_entries(DOMAIN):
            coordinator = entry.runtime_data
            await coordinator.log_weight(weight, unit, notes)
            break
    
    # Register services if not already registered
    if not hass.services.has_service(DOMAIN, SERVICE_LOG_FEEDING):
        hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_FEEDING,
            log_feeding,
            schema=vol.Schema({
                vol.Required("food_type"): cv.string,
                vol.Required("food_size"): cv.string,
                vol.Optional("notes", default=""): cv.string,
            })
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_LOG_SHEDDING):
        hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_SHEDDING,
            log_shedding,
            schema=vol.Schema({
                vol.Required("complete"): cv.boolean,
                vol.Optional("notes", default=""): cv.string,
            })
        )
    
    if not hass.services.has_service(DOMAIN, SERVICE_LOG_WEIGHT):
        hass.services.async_register(
            DOMAIN,
            SERVICE_LOG_WEIGHT,
            log_weight,
            schema=vol.Schema({
                vol.Required("weight"): vol.All(vol.Coerce(float), vol.Range(min=0)),
                vol.Optional("unit", default="g"): vol.In(["g", "kg", "oz", "lb"]),
                vol.Optional("notes", default=""): cv.string,
            })
        )

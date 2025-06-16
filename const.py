"""Constants for the Reptile Habitat Manager integration."""
from homeassistant.const import Platform

DOMAIN = "reptile_habitat"

# Platforms
PLATFORMS = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
]

# Configuration keys
CONF_REPTILE_NAME = "reptile_name"
CONF_HEAT_SOURCES = "heat_sources"

# Heat source keys
CONF_HEAT_NAME = "name"
CONF_HEAT_SWITCH = "switch_entity"
CONF_HEAT_SENSOR = "temp_sensor"
CONF_TARGET_MIN = "target_min"
CONF_TARGET_MAX = "target_max" 
CONF_CRITICAL_MIN = "critical_min"
CONF_CRITICAL_MAX = "critical_max"

# Atmosphere keys
CONF_ATMO_TEMP_SENSOR = "atmo_temp_sensor"
CONF_ATMO_HUMIDITY_SENSOR = "atmo_humidity_sensor"
CONF_ATMO_TARGET_MIN_TEMP = "atmo_target_min_temp"
CONF_ATMO_TARGET_MAX_TEMP = "atmo_target_max_temp"
CONF_ATMO_CRITICAL_MIN_TEMP = "atmo_critical_min_temp"
CONF_ATMO_CRITICAL_MAX_TEMP = "atmo_critical_max_temp"
CONF_ATMO_TARGET_MIN_HUMIDITY = "atmo_target_min_humidity"
CONF_ATMO_TARGET_MAX_HUMIDITY = "atmo_target_max_humidity"
CONF_ATMO_CRITICAL_MIN_HUMIDITY = "atmo_critical_min_humidity"
CONF_ATMO_CRITICAL_MAX_HUMIDITY = "atmo_critical_max_humidity"

# Services
SERVICE_LOG_FEEDING = "log_feeding"
SERVICE_LOG_SHEDDING = "log_shedding"
SERVICE_LOG_WEIGHT = "log_weight"

# Default values
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_NOTIFICATION_COOLDOWN = 30  # minutes

# Status values
STATUS_OK = "ok"
STATUS_HEATING = "heating"
STATUS_COOLING = "cooling"
STATUS_CRITICAL_LOW = "critical_low"
STATUS_CRITICAL_HIGH = "critical_high"
STATUS_BELOW_TARGET = "below_target"
STATUS_ABOVE_TARGET = "above_target"
STATUS_UNKNOWN = "unknown"

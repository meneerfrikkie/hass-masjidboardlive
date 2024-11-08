import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN, CONF_MASJID_BOARD_URL, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
from .coordinator import SalaahTimesCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize the component (this is required by Home Assistant)."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Masjid Board Live from a config entry."""
    # Load configuration from the entry
    masjid_board_url = entry.data[CONF_MASJID_BOARD_URL]
    poll_interval = entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

    # Initialize and store the coordinator for this entry
    coordinator = SalaahTimesCoordinator(hass, masjid_board_url, poll_interval)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator under a unique entry ID in hass.data
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to the sensor platform
    hass.config_entries.async_setup_platforms(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Remove the coordinator from hass.data
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)

    # Unload the sensor platform
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    return unload_ok
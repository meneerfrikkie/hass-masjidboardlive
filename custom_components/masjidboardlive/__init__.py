import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import timedelta
from aiohttp import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, CONF_MASJID_BOARD_URL, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, PRAYERS

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Salaah Times component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Salaah Times from a config entry for each masjid."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    masjid_board_url = entry.data[CONF_MASJID_BOARD_URL]
    poll_interval = entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

    # Create a unique coordinator for each masjid
    coordinator = SalaahTimesCoordinator(hass, masjid_board_url, poll_interval)
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator under a unique ID
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Extract the masjid name to use as the device name
    masjid_name = coordinator.data.get("masjid_name", "Unknown Masjid")

    # Register sensors for each prayer time with masjid name as device
    for prayer in PRAYERS:
        hass.helpers.discovery.load_platform("sensor", DOMAIN, {
            "prayer": prayer,
            "coordinator": coordinator,
            "masjid_name": masjid_name,
            "entry_id": entry.entry_id,
        }, entry)

    # Access the device registry and create a device entry for this masjid
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        manufacturer="Masjid Board",
        name=masjid_name,  # Use the masjid name as the device name
    )

    return True

class SalaahTimesCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, update_interval):
        """Initialize the coordinator."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=update_interval))
        self.hass = hass
        self.url = url

    async def _async_update_data(self):
        """Fetch data from the masjid board URL."""
        return await self.get_salaah_times()

    async def get_salaah_times(self):
        """Scrape salaah times and masjid name from the masjid board."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        
        try:
            async with session.get(self.url, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Extract masjid name
                masjid_name_element = soup.find('h1', id='masjidName2')
                if not masjid_name_element:
                    _LOGGER.error("Masjid name element not found on the page")
                    return {}

                masjid_name = masjid_name_element.text.strip()

                # Extract prayer times
                salaah_times = {"masjid_name": masjid_name}
                for prayer, prayer_id in PRAYERS.items():
                    athan_element = soup.find('h5', id=f'{prayer_id}Athan')
                    jamaah_element = soup.find('h5', id=f'{prayer_id}Jamaah')
                    if not athan_element or not jamaah_element:
                        _LOGGER.warning(f"Prayer times for {prayer} not found on the page")
                        salaah_times[prayer] = {'Adhan': None, 'Jamaah': None}
                    else:
                        salaah_times[prayer] = {
                            'Adhan': athan_element.text.strip(),
                            'Jamaah': jamaah_element.text.strip()
                        }

                return salaah_times

        except ClientError as e:
            _LOGGER.error(f"Error fetching salaah times from URL {self.url}: {e}")
            return {}
        except Exception as e:
            _LOGGER.exception("Unexpected error in get_salaah_times:")
            return {}
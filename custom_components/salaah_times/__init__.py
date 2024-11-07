import logging
import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant import config_entries
from .const import DOMAIN, CONF_MASJID_BOARD_URL, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, PRAYERS
from .config_flow import SalaahTimesFlowHandler

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Salaah Times component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Salaah Times from a config entry."""
    masjid_board_url = entry.data[CONF_MASJID_BOARD_URL]
    poll_interval = entry.data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

    # Create and initialize the coordinator
    coordinator = SalaahTimesCoordinator(hass, masjid_board_url, poll_interval)
    await coordinator.async_config_entry_first_refresh()

    # Register sensors for each prayer time with the masjid name prefix
    masjid_name = coordinator.data.get("masjid_name", "Unknown Masjid")
    for prayer in PRAYERS:
        hass.helpers.discovery.load_platform("sensor", DOMAIN, {
            "prayer": prayer,
            "coordinator": coordinator,
            "masjid_name": masjid_name
        }, entry)

    return True

class SalaahTimesCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, url, update_interval):
        """Initialize the coordinator."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=update_interval))
        self.url = url

    async def _async_update_data(self):
        """Fetch data from the masjid board URL."""
        return await self.hass.async_add_executor_job(self.get_salaah_times)

    def get_salaah_times(self):
        """Scrape salaah times and masjid name from the masjid board."""
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract masjid name
        masjid_name = soup.find('h1', id='masjidName2').text.strip()

        # Extract prayer times
        salaah_times = {"masjid_name": masjid_name}
        for prayer, prayer_id in PRAYERS.items():
            athan_time = soup.find('h5', id=f'{prayer_id}Athan').text.strip()
            jamaah_time = soup.find('h5', id=f'{prayer_id}Jamaah').text.strip()
            salaah_times[prayer] = {'Adhan': athan_time, 'Jamaah': jamaah_time}

        return salaah_times

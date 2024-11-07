import logging
import requests  # Add this line to import the requests library
from bs4 import BeautifulSoup
import voluptuous as vol
from datetime import timedelta
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .const import DOMAIN, CONF_MASJID_BOARD_URL, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL, PRAYERS
from .sensor import SalaahTimesSensor

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_MASJID_BOARD_URL): cv.url,
        vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): cv.positive_int,
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Salaah Times component."""
    conf = config[DOMAIN]
    url = conf[CONF_MASJID_BOARD_URL]
    poll_interval = conf.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)

    # Create and initialize the coordinator
    coordinator = SalaahTimesCoordinator(hass, url, poll_interval)
    await coordinator.async_config_entry_first_refresh()

    # Register sensors for each prayer time with the masjid name prefix
    masjid_name = coordinator.data.get("masjid_name", "Unknown Masjid")
    for prayer in PRAYERS:
        hass.helpers.discovery.load_platform("sensor", DOMAIN, {
            "prayer": prayer,
            "coordinator": coordinator,
            "masjid_name": masjid_name
        }, config)

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

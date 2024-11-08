import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, PRAYERS
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

class SalaahTimesCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, url: str, update_interval: int):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=update_interval))
        self.url = url

    async def _async_update_data(self):
        session = aiohttp_client.async_get_clientsession(self.hass)
        try:
            async with session.get(self.url, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()
                return self._parse_html(html)
        except Exception as error:
            _LOGGER.error(f"Error fetching data from {self.url}: {error}")
            return {}

    def _parse_html(self, html: str) -> dict:
        soup = BeautifulSoup(html, 'html.parser')
        masjid_name = soup.find('h1', id='masjidName2')
        data = {"masjid_name": masjid_name.text.strip() if masjid_name else "Unknown Masjid"}

        for prayer, prayer_id in PRAYERS.items():
            athan = soup.find('h5', id=f'{prayer_id}Athan')
            jamaah = soup.find('h5', id=f'{prayer_id}Jamaah')
            data[prayer] = {
                "Adhan": athan.text.strip() if athan else None,
                "Jamaah": jamaah.text.strip() if jamaah else None
            }
        return data
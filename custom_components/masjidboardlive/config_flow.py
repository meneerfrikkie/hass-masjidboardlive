import logging
from homeassistant import config_entries
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, CONF_MASJID_BOARD_URL, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
import voluptuous as vol
import aiohttp
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

class SalaahTimesFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input:
            errors = {}
            url = user_input[CONF_MASJID_BOARD_URL]

            if not await self._is_valid_url(url):
                errors["base"] = "invalid_url"
            if not errors:
                return self.async_create_entry(
                    title="Masjid Board Live",
                    data={
                        CONF_MASJID_BOARD_URL: url,
                        CONF_POLL_INTERVAL: user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
                    }
                )
            return self.async_show_form(
                step_id="user",
                data_schema=self._schema(),
                errors=errors,
            )

        return self.async_show_form(step_id="user", data_schema=self._schema())

    def _schema(self):
        return vol.Schema({
            vol.Required(CONF_MASJID_BOARD_URL): str,
            vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
        })

    async def _is_valid_url(self, url: str) -> bool:
        session = aiohttp_client.async_get_clientsession(self.hass)
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return False
                html = await response.text()
                return BeautifulSoup(html, "html.parser").find(id="masjidName2") is not None
        except aiohttp.ClientError:
            _LOGGER.error(f"Invalid URL or unreachable: {url}")
            return False
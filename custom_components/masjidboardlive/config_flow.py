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
        """Handle the initial step for user input and masjid name retrieval."""
        if user_input:
            errors = {}
            url = user_input[CONF_MASJID_BOARD_URL]

            # Fetch masjid name before creating the config entry
            masjid_name = await self._fetch_masjid_name(url)
            if not masjid_name:
                errors["base"] = "invalid_url"
            if not errors:
                return self.async_create_entry(
                    title=masjid_name,  # Use the fetched masjid name as the title
                    data={
                        CONF_MASJID_BOARD_URL: url,
                        CONF_POLL_INTERVAL: user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL)
                    }
                )
            # Show form with errors if URL is invalid
            return self.async_show_form(
                step_id="user",
                data_schema=self._schema(),
                errors=errors,
            )

        # Show the form initially
        return self.async_show_form(step_id="user", data_schema=self._schema())

    def _schema(self):
        """Return the schema for user input."""
        return vol.Schema({
            vol.Required(CONF_MASJID_BOARD_URL): str,
            vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
        })

    async def _fetch_masjid_name(self, url: str) -> str | None:
        """Attempt to fetch the masjid name from the provided URL."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    _LOGGER.error(f"Failed to fetch URL {url}, status: {response.status}")
                    return None

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                masjid_name_element = soup.find("h1", id="masjidName2")
                if masjid_name_element:
                    return masjid_name_element.text.strip()
                else:
                    _LOGGER.error("Masjid name element not found on the page.")
                    return None
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Error accessing Masjid board URL '{url}': {e}")
            return None
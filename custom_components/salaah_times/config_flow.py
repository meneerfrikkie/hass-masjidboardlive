import logging
import aiohttp
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from .const import DOMAIN, CONF_MASJID_BOARD_URL, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

class SalaahTimesFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Salaah Times."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the user input during the configuration."""
        if user_input is not None:
            masjid_board_url = user_input[CONF_MASJID_BOARD_URL]
            session = aiohttp_client.async_get_clientsession(self.hass)

            # Asynchronous URL validation and fetching masjid name with aiohttp
            try:
                async with session.get(masjid_board_url, timeout=10) as response:
                    if response.status != 200:
                        _LOGGER.error(f"Received status code {response.status} for URL {masjid_board_url}")
                        raise ValueError("Failed to reach the Masjid board URL")
                    
                    # Parse the HTML to extract the masjid name
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    masjid_name_element = soup.find('h1', id='masjidName2')
                    
                    if not masjid_name_element:
                        _LOGGER.error("Masjid name element not found on the page")
                        raise ValueError("Failed to retrieve the masjid name from the page")
                    
                    masjid_name = masjid_name_element.text.strip()
            
            except aiohttp.ClientError as e:
                _LOGGER.error(f"Error accessing Masjid board URL '{masjid_board_url}': {e}")
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_schema(),
                    errors={"base": "invalid_url"}
                )
            except Exception as e:
                _LOGGER.exception("Unexpected error occurred during configuration flow:")
                return self.async_show_form(
                    step_id="user",
                    data_schema=self._get_schema(),
                    errors={"base": "unknown_error"}
                )

            # Proceed with the configuration, using the masjid name as the entry title
            return self.async_create_entry(
                title=masjid_name,  # Use the fetched masjid name as the title
                data={
                    CONF_MASJID_BOARD_URL: masjid_board_url,
                    CONF_POLL_INTERVAL: user_input.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                }
            )
        
        # Show the form to the user if no input is provided
        return self.async_show_form(
            step_id="user",
            data_schema=self._get_schema(),
        )

    def _get_schema(self):
        """Return the schema for the user input form."""
        return vol.Schema({
            vol.Required(CONF_MASJID_BOARD_URL): str,
            vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
        })
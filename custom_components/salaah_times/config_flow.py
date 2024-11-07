import logging
import requests
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_MASJID_BOARD_URL, CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL

_LOGGER = logging.getLogger(__name__)

class SalaahTimesFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Salaah Times."""
    
    VERSION = 1

    def __init__(self):
        """Initialize the flow."""
        self.masjid_board_url = None

    async def async_step_user(self, user_input=None):
        """Handle the user input during the configuration."""
        if user_input is not None:
            # Validate the provided URL (masjid board URL)
            masjid_board_url = user_input[CONF_MASJID_BOARD_URL]
            
            # Verify that the URL is reachable
            try:
                response = requests.get(masjid_board_url)
                if response.status_code != 200:
                    raise ValueError("Failed to reach the Masjid board URL")
            except Exception as e:
                _LOGGER.error(f"Error accessing Masjid board URL: {e}")
                return self.async_show_form(
                    step_id="user",
                    data=user_input,
                    errors={"base": "invalid_url"}
                )

            # Proceed with the configuration if the URL is valid
            return self.async_create_entry(
                title="Salaah Times",
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

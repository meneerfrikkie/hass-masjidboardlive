from homeassistant.helpers.entity import Entity
from .const import DOMAIN, PRAYERS

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Salaah Times sensor platform for each masjid as a unique device."""
    if discovery_info is None:
        return

    prayer = discovery_info["prayer"]
    coordinator = discovery_info["coordinator"]
    masjid_name = discovery_info["masjid_name"]
    entry_id = discovery_info["entry_id"]

    async_add_entities([
        SalaahTimesSensor(coordinator, masjid_name, prayer, "Adhan", entry_id),
        SalaahTimesSensor(coordinator, masjid_name, prayer, "Jamaah", entry_id)
    ])


class SalaahTimesSensor(Entity):
    """Representation of a Salaah Times sensor."""

    def __init__(self, coordinator, masjid_name, prayer, time_type, entry_id):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.masjid_name = masjid_name
        self.prayer = prayer
        self.time_type = time_type
        self.entry_id = entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.masjid_name} {self.prayer} {self.time_type} Time"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.prayer][self.time_type]

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self.entry_id}_{self.prayer}_{self.time_type}"

    @property
    def device_info(self):
        """Return device information to group sensors under the masjid device."""
        return {
            "identifiers": {(DOMAIN, self.entry_id)},
            "name": self.masjid_name,
            "manufacturer": "Masjid Board",
            "entry_type": "service",
            "config_entry_id": self.entry_id  # Ensures each entity is linked to the masjid device
        }

    @property
    def should_poll(self):
        """Disable polling for this sensor."""
        return False

    async def async_update(self):
        """Update the sensor with the latest data."""
        await self.coordinator.async_request_refresh()
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, PRAYERS

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    masjid_name = coordinator.data.get("masjid_name", "Unknown Masjid")

    entities = []
    for prayer in PRAYERS:
        for time_type in ["Adhan", "Jamaah"]:
            entities.append(SalaahTimesSensor(coordinator, masjid_name, prayer, time_type, config_entry.entry_id))
    async_add_entities(entities)

class SalaahTimesSensor(Entity):
    """Representation of a Salaah Times sensor."""

    ICONS = {
        "Fajr_Adhan": "mdi:weather-sunset-up",
        "Fajr_Jamaah": "mdi:clock-outline",
        "Zuhr_Adhan": "mdi:weather-sunny",
        "Zuhr_Jamaah": "mdi:clock-outline",
        "Asr_Adhan": "mdi:weather-partly-cloudy",
        "Asr_Jamaah": "mdi:clock-outline",
        "Maghrib_Adhan": "mdi:weather-sunset-down",
        "Maghrib_Jamaah": "mdi:clock-outline",
        "Isha_Adhan": "mdi:weather-night",
        "Isha_Jamaah": "mdi:clock-outline",
    }

    def __init__(self, coordinator, masjid_name, prayer, time_type, entry_id):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.masjid_name = masjid_name
        self.prayer = prayer
        self.time_type = time_type
        self._unique_id = f"{entry_id}_{prayer}_{time_type}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.masjid_name} {self.prayer} {self.time_type}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.prayer, {}).get(self.time_type)

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return self._unique_id

    @property
    def icon(self):
        """Return the icon for this sensor based on prayer and time type."""
        icon_key = f"{self.prayer}_{self.time_type}"
        return self.ICONS.get(icon_key, "mdi:clock")

    @property
    def should_poll(self):
        """Disable polling for this sensor."""
        return False

    async def async_update(self):
        """Update the sensor with the latest data."""
        await self.coordinator.async_request_refresh()
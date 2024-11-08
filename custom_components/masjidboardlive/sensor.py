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
    def __init__(self, coordinator, masjid_name, prayer, time_type, entry_id):
        self.coordinator = coordinator
        self.masjid_name = masjid_name
        self.prayer = prayer
        self.time_type = time_type
        self._unique_id = f"{entry_id}_{prayer}_{time_type}"
    
    @property
    def name(self):
        return f"{self.masjid_name} {self.prayer} {self.time_type}"

    @property
    def state(self):
        return self.coordinator.data.get(self.prayer, {}).get(self.time_type)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def should_poll(self):
        return False

    async def async_update(self):
        await self.coordinator.async_request_refresh()
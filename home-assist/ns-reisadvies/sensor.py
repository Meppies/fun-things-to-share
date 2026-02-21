import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.exceptions import ConfigEntryNotReady
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensoren via de UI Config Entry."""
    # Controleer of de coordinator klaar staat in hass.data
    if DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]:
        raise ConfigEntryNotReady("Wachten op NS Coordinator")

    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Voeg de sensor toe en koppel deze aan de bestaande coordinator
    async_add_entities([
        NSReisadviesSensor(coordinator, entry.title, entry.entry_id)
    ])
    return True

class NSReisadviesSensor(CoordinatorEntity, SensorEntity):
    """Sensor die de data van de coordinator doorgeeft aan de kaart."""
    def __init__(self, coordinator, name, unique_id):
        super().__init__(coordinator)
        self._name = name
        self._unique_id = unique_id

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def state(self):
        """De status van de sensor (bijv. de eerste vertrektijd)."""
        if self.coordinator.data and len(self.coordinator.data) > 0:
            try:
                # Pak de geplande vertrektijd van de eerste rit
                return self.coordinator.data[0]["legs"][0]["origin"]["plannedDateTime"]
            except (Key_Error, IndexError):
                return "Data aanwezig"
        return "Geen ritten"

    @property
    def extra_state_attributes(self):
        """Dit is de 'trips' lijst die de JavaScript kaart uitleest."""
        # We geven de data 1-op-1 door. De JS kaart doet de rest.
        # Hierdoor blijven ook de kilometers (distanceInMeters) behouden.
        return {
            "trips": self.coordinator.data if self.coordinator.data else [],
            "friendly_name": self._name
        }
import logging
import voluptuous as vol
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    if DOMAIN not in hass.data or entry.entry_id not in hass.data[DOMAIN]:
        raise ConfigEntryNotReady("Wachten op NS Coordinator")

    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensor = NSReisadviesSensor(coordinator, entry.title, entry.entry_id)
    async_add_entities([sensor])

    platform = entity_platform.async_get_current_platform()
    # Service voor Hartje AAN
    platform.async_register_entity_service(
        "track_trip", {"ctx_recon": cv.string}, "async_track_trip"
    )
    # Service voor Hartje UIT
    platform.async_register_entity_service(
        "untrack_trip", {"ctx_recon": cv.string}, "async_untrack_trip"
    )

    return True

class NSReisadviesSensor(CoordinatorEntity, SensorEntity):
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
        if self.coordinator.data and len(self.coordinator.data) > 0:
            try:
                return self.coordinator.data[0]["legs"][0]["origin"]["plannedDateTime"]
            except (KeyError, IndexError):
                return "Data aanwezig"
        return "Geen ritten"

    @property
    def extra_state_attributes(self):
        # We geven hier de trips door EN de lijst met actieve hartjes!
        return {
            "trips": self.coordinator.data if self.coordinator.data else [],
            "tracked_trips": list(self.coordinator.tracked_trips) if hasattr(self.coordinator, 'tracked_trips') else [],
            "friendly_name": self._name
        }

    async def async_track_trip(self, ctx_recon):
        if hasattr(self.coordinator, 'track_trip'):
            self.coordinator.track_trip(ctx_recon)
            
    async def async_untrack_trip(self, ctx_recon):
        if hasattr(self.coordinator, 'untrack_trip'):
            self.coordinator.untrack_trip(ctx_recon)
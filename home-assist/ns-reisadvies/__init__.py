import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN
# Haal onze superslimme nieuwe coordinator op
from .coordinator import NSUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Start de integratie en registreer het pad voor de kaart."""
    
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    api_key = entry.options.get("api_key", entry.data.get("api_key"))
    act_station = entry.data.get("act_station")
    arr_station = entry.data.get("arr_station")
    
    # Gebruik nu de asynchrone coordinator uit coordinator.py!
    coordinator = NSUpdateCoordinator(hass, api_key, act_station, arr_station)

    # Forceer de eerste verversing van data
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # REGISTRATIE VAN HET STATISCHE PAD (Voor de kaart)
    if "static_paths_registered" not in hass.data[DOMAIN]:
        path = hass.config.path("custom_components/ns_reisadvies/www")
        if os.path.isdir(path):
            await hass.http.async_register_static_paths([
                StaticPathConfig(
                    url_path="/ns_reisadvies",
                    path=path,
                    cache_headers=False 
                )
            ])
            hass.data[DOMAIN]["static_paths_registered"] = True
            _LOGGER.info("Pad /ns_reisadvies geregistreerd voor de kaart.")

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Verwijder de integratie."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
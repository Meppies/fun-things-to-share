import logging
import os
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.components.http import StaticPathConfig

from .const import DOMAIN 

try:
    from .api import NSAPI
except ImportError:
    from api import NSAPI

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Start de integratie en registreer het pad voor de kaart."""
    
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    api_key = entry.options.get("api_key", entry.data.get("api_key"))
    act_station = entry.data.get("act_station")
    arr_station = entry.data.get("arr_station")
    
    scan_interval = entry.options.get("scan_interval_minuten", 5)

    api = NSAPI(api_key)

    async def async_update_data():
        try:
            # Deze functie haalt de trips op en zorgt dat distanceInMeters mee komt
            return await hass.async_add_executor_job(
                api.get_trips, act_station, arr_station
            )
        except Exception as err:
            raise UpdateFailed(f"Fout bij ophalen NS data: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"NS {act_station} -> {arr_station}",
        update_method=async_update_data,
        update_interval=timedelta(minutes=scan_interval),
    )

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
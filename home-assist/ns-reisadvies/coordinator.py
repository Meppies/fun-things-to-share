"""DataUpdateCoordinator for NS Reisadvies."""
from datetime import timedelta, datetime
import logging

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import API_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

class NSUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching NS data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api_key: str,
        from_station: str,
        to_station: str,
    ) -> None:
        """Initialize."""
        self.api_key = api_key
        # Let op: zorg dat deze namen (from_station/to_station) 
        # in sensor.py ook zo worden doorgegeven.
        self.from_station = from_station
        self.to_station = to_station

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5), # Update elke 5 minuten
        )

    async def _async_update_data(self):
        """Fetch data from NS API."""
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        
        # De API vereist een dateTime parameter voor actuele trips
        params = {
            "fromStation": self.from_station,
            "toStation": self.to_station,
            "dateTime": datetime.now().isoformat()
        }

        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        API_URL, headers=headers, params=params
                    ) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error communicating with API: {response.status}")
                        
                        data = await response.json()
                        return data.get("trips", [])
                        
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
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

TRIP_API_URL = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips/trip"

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
        self.api_key = api_key
        self.from_station = from_station
        self.to_station = to_station
        
        # Dit is het centrale geheugen voor alle apparaten!
        self.tracked_trips = set()

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )

    def track_trip(self, ctx_recon: str):
        """Zet een hartje AAN."""
        if ctx_recon not in self.tracked_trips:
            self.tracked_trips.add(ctx_recon)
            self.hass.async_create_task(self.async_request_refresh())

    def untrack_trip(self, ctx_recon: str):
        """Zet een hartje UIT."""
        if ctx_recon in self.tracked_trips:
            self.tracked_trips.discard(ctx_recon)
            self.hass.async_create_task(self.async_request_refresh())

    async def _async_update_data(self):
        headers = {"Ocp-Apim-Subscription-Key": self.api_key}
        params = {
            "fromStation": self.from_station,
            "toStation": self.to_station,
            "dateTime": datetime.now().isoformat()
        }

        try:
            async with async_timeout.timeout(20):
                async with aiohttp.ClientSession() as session:
                    # 1. Normale ritten
                    async with session.get(API_URL, headers=headers, params=params) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"Error communicating with API: {response.status}")
                        data = await response.json()
                        normal_trips = data.get("trips", [])
                        
                    # 2. Favoriete ritten (VIP)
                    tracked_trips_data = []
                    trips_to_remove = set()
                    
                    for ctx_recon in list(self.tracked_trips):
                        trip_params = {"ctxRecon": ctx_recon}
                        async with session.get(TRIP_API_URL, headers=headers, params=trip_params) as trip_resp:
                            if trip_resp.status == 200:
                                trip_data = await trip_resp.json()
                                tracked_trips_data.append(trip_data)
                            elif trip_resp.status in [400, 404]:
                                # NS kent de rit niet meer, verwijder hem uit het geheugen
                                trips_to_remove.add(ctx_recon)

                    # Opschonen
                    for ctx in trips_to_remove:
                        self.tracked_trips.discard(ctx)

                    # 3. Samenvoegen
                    all_trips = normal_trips
                    normal_ctx_recons = [t.get("ctxRecon") for t in normal_trips if "ctxRecon" in t]
                    
                    for tracked_trip in tracked_trips_data:
                        if tracked_trip.get("ctxRecon") not in normal_ctx_recons:
                            all_trips.append(tracked_trip)
                            
                    all_trips.sort(key=lambda x: x.get("legs", [{}])[0].get("origin", {}).get("plannedDateTime", ""))
                            
                    return all_trips
                        
        except Exception as err:
            raise UpdateFailed(f"Error communicating with NS API: {err}")
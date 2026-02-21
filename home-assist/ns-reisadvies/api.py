import requests
import logging

_LOGGER = logging.getLogger(__name__)

class NSAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        # De officiële NS API v3 URL voor reisadviezen
        self.base_url = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips"

    def get_trips(self, act_station, arr_station):
        """Haal reisadviezen op van A naar B."""
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        params = {
            "fromStation": act_station,
            "toStation": arr_station,
            "previousAdvices": 0,
            "nextAdvices": 8,  # We halen er ruim voldoende op (de kaart filtert later)
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status() # Geeft een foutmelding als de statuscode niet 200 is
            
            data = response.json()
            
            # Check of er daadwerkelijk reizen in het antwoord zitten
            if "trips" in data:
                return data["trips"]
            else:
                _LOGGER.warning(f"Geen reizen gevonden tussen {act_station} en {arr_station}")
                return []

        except requests.exceptions.RequestException as err:
            _LOGGER.error(f"Fout bij verbinden met NS API: {err}")
            return []
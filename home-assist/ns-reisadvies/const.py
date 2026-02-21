"""Constants for the NS Reisadvies integration."""

DOMAIN = "ns_reisadvies"
NAME = "NS Reisadvies"

# Zorg dat deze namen exact overeenkomen met wat je in de config_flow gebruikt
CONF_API_KEY = "api_key"
CONF_FROM_STATION = "act_station"
CONF_TO_STATION = "arr_station"

# API URL
API_URL = "https://gateway.apiportal.ns.nl/reisinformatie-api/api/v3/trips"
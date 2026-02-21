import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

# Importeer DOMAIN uit je const.py
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Een hardcoded lijst van alle Nederlandse treinstations (Alfabetisch)
STATIONS = [
    "'t Harde", "Aalten", "Abcoude", "Akkrum", "Alkmaar", "Alkmaar Noord", "Almelo", "Almelo de Riet",
    "Almere Buiten", "Almere Centrum", "Almere Muziekwijk", "Almere Oostvaarders", "Almere Parkwijk", "Almere Poort",
    "Alphen a/d Rijn", "Amersfoort Centraal", "Amersfoort Schothorst", "Amersfoort Vathorst", "Amstelveen",
    "Amsterdam Amstel", "Amsterdam Arena", "Amsterdam Bijlmer Arena", "Amsterdam Centraal", "Amsterdam Holendrecht",
    "Amsterdam Lelylaan", "Amsterdam Muiderpoort", "Amsterdam RAI", "Amsterdam Science Park", "Amsterdam Sloterdijk",
    "Amsterdam Zuid", "Anna Paulowna", "Apeldoorn", "Apeldoorn De Maten", "Apeldoorn Osseveld", "Appingedam",
    "Arnemuiden", "Arnhem Centraal", "Arnhem Presikhaaf", "Arnhem Velperpoort", "Arnhem Zuid", "Assen",
    "Baarn", "Baflo", "Barendrecht", "Barneveld Centrum", "Barneveld Noord", "Barneveld Zuid", "Bedum",
    "Beek-Elsloo", "Beesd", "Beilen", "Bergen op Zoom", "Best", "Beverwijk", "Bilthoven", "Blerick",
    "Bloemendaal", "Bodegraven", "Borne", "Boskoop", "Boskoop Snijdelwijk", "Bovenkarspel Flora",
    "Bovenkarspel-Grootebroek", "Boxmeer", "Boxtel", "Breda", "Breda-Prinsenbeek", "Breukelen", "Brouwhuis",
    "Buitenpost", "Buitens", "Bunde", "Bunnik", "Bussum Zuid", "Capelle Schollevaar", "Castricum",
    "Chevremont", "Coevorden", "Cuijk", "Culemborg", "Daarlerveen", "Dalen", "Dalfsen", "De Vink",
    "De Westereen", "Deinum", "Delden", "Delft", "Delft Campus", "Delfzijl", "Delfzijl West", "Den Dolder",
    "Den Haag Centraal", "Den Haag HS", "Den Haag Laan v NOI", "Den Haag Mariahoeve", "Den Haag Moerwijk",
    "Den Haag Ypenburg", "Den Helder", "Den Helder Zuid", "Deurne", "Deventer", "Deventer Colmschate",
    "Didam", "Diemen", "Diemen Zuid", "Dieren", "Doetinchem", "Doetinchem De Huet", "Dordrecht",
    "Dordrecht Stadspolders", "Dordrecht Zuid", "Driebergen-Zeist", "Driehuis", "Dronten", "Dronryp",
    "Duiven", "Duivendrecht", "Echt", "Ede Centrum", "Ede-Wageningen", "Eemshaven", "Eijsden",
    "Eindhoven Centraal", "Eindhoven Strijp-S", "Elst", "Emmen", "Emmen Zuid", "Enkhuizen", "Enschede",
    "Enschede Kennispark", "Enschede De Eschmarke", "Ermelo", "Etten-Leur", "Eygelshoven", "Eygelshoven Markt",
    "Feanwalden", "Gaanderen", "Geldermalsen", "Geldrop", "Geleen Oost", "Geleen-Lutterade", "Gilze-Rijen",
    "Glanerbrug", "Goes", "Goor", "Gorinchem", "Gouda", "Gouda Goverwelle", "Gramsbergen", "Grijpskerk",
    "Groningen", "Groningen Europapark", "Groningen Noord", "Grou-Jirnsum", "Haarlem", "Haarlem Spaarnwoude",
    "Halfweg-Zwanenburg", "Hardenberg", "Harderwijk", "Hardinxveld Blauwe Zoom", "Hardinxveld-Giessendam",
    "Haren", "Harlingen", "Harlingen Haven", "Heemskerk", "Heemstede-Aerdenhout", "Heerenveen",
    "Heerenveen IJsstadion", "Heerhugowaard", "Heerlen", "Heerlen Woonboulevard", "Heeze", "Heiloo",
    "Heino", "Helmond", "Helmond Brandevoort", "Helmond 't Hout", "Helmond Brouwhuis", "Hemmen-Dodewaard",
    "Hengelo", "Hengelo Gezondheidspark", "Hengelo Oost", "Hillegom", "Hilversum", "Hilversum Media Park",
    "Hilversum Sportpark", "Hindeloopen", "Hoensbroek", "Hoevelaken", "Holten", "Hoofddorp", "Hoogeveen",
    "Hoogezand-Sappemeer", "Hoogkarspel", "Hoogkarspel", "Hoorn", "Hoorn Kersenboogerd", "Horst-Sevenum", "Houten",
    "Houten Castellum", "Houthem-St. Gerlach", "Hurdegaryp", "IJlst", "IJmuiden", "Kampen", "Kampen Zuid",
    "Kapelle-Biezelinge", "Kerkrade Centrum", "Kesteren", "Klarenbeek", "Klimmen-Ransdaal", "Koog aan de Zaan",
    "Koudum-Molkwerum", "Krabbendijke", "Krommenie-Assendelft", "Kropswolde", "Kruiningen-Yerseke",
    "Lansingerland-Zoetermeer", "Landgraaf", "Leerdam", "Leeuwarden", "Leeuwarden Camminghaburen", "Leiden Centraal",
    "Leiden Lammenschans", "Lelystad Centrum", "Lichtenvoorde-Groenlo", "Lochem", "Loppersum", "Lunteren",
    "Maarheeze", "Maarn", "Maarssen", "Maastricht", "Maastricht Noord", "Maastricht Randwyck", "Mantgum",
    "Marienberg", "Martenshoek", "Meerssen", "Meppel", "Middelburg", "Mook-Molenhoek", "Naarden-Bussum",
    "Nieuw Amsterdam", "Nieuw Vennep", "Nieuwerkerk a/d IJssel", "Nijkerk", "Nijmegen", "Nijmegen Dukenburg",
    "Nijmegen Goffert", "Nijmegen Heyendaal", "Nijmegen Lent", "Nijverdal", "Nunspeet", "Nuth", "Obdam",
    "Oisterwijk", "Oldenzaal", "Olst", "Ommen", "Oosterbeek", "Opheusden", "Oss", "Oss West", "Oudenbosch",
    "Overveen", "Purmerend", "Purmerend Overwhere", "Purmerend Weidevenne", "Putten", "Raalte", "Ravenstein",
    "Reuver", "Rheden", "Rhenen", "Rijssen", "Rilland-Bath", "Roermond", "Roodeschool", "Roosendaal",
    "Rosmalen", "Rotterdam Alexander", "Rotterdam Blaak", "Rotterdam Centraal", "Rotterdam Lombardijen",
    "Rotterdam Noord", "Rotterdam Stadion", "Rotterdam Zuid", "Ruurlo", "Santpoort Noord", "Santpoort Zuid",
    "Sappemeer Oost", "Sassenheim", "Sauwerd", "Schagen", "Scheemda", "Schiedam Centrum", "Schin op Geul",
    "Schinnen", "Schiphol Airport", "Sittard", "Sliedrecht", "Sliedrecht Baanhoek", "Sneek", "Sneek Noord",
    "Soest", "Soest Zuid", "Soestdijk", "Spaubeek", "Stavoren", "Stedum", "Steenwijk", "Stein", "Susteren",
    "Swalmen", "Tegelen", "Terborg", "Tiel", "Tiel Passewaaij", "Tilburg", "Tilburg Reeshof",
    "Tilburg Universiteit", "Twello", "Uitgeest", "Uithuizen", "Uithuizermeeden", "Utrecht Centraal",
    "Utrecht Leidsche Rijn", "Utrecht Lunetten", "Utrecht Maliebaan", "Utrecht Overvecht", "Utrecht Terwijde",
    "Utrecht Vaartsche Rijn", "Utrecht Zuilen", "Valkenburg", "Varsseveld", "Veendam", "Veenendaal Centrum",
    "Veenendaal West", "Veenendaal-De Klomp", "Velp", "Venlo", "Venray", "Vierlingsbeek", "Vleuten",
    "Vlissingen", "Vlissingen Souburg", "Voerendaal", "Voorburg", "Voorhout", "Voorschoten", "Voorst-Empe",
    "Vorden", "Vriezenveen", "Vroomshoop", "Vught", "Waddinxveen", "Waddinxveen Noord", "Waddinxveen Triangel",
    "Warffum", "Weert", "Weesp", "Wehl", "Westervoort", "Wezep", "Wierden", "Wijchen", "Wijhe", "Winschoten",
    "Winsum", "Winterswijk", "Winterswijk West", "Woerden", "Wolfheze", "Wolvega", "Workum", "Wormerveer",
    "Zaandam", "Zaandam Kogerveld", "Zaandijk Zaanse Schans", "Zaltbommel", "Zandvoort aan Zee", "Zetten-Andelst",
    "Zevenaar", "Zevenbergen", "Zoetermeer", "Zoetermeer Oost", "Zuidbroek", "Zuidhorn", "Zutphen", "Zwolle",
    "Zwolle Stadshagen", "Zwijndrecht"
]

class NSReisadviesOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        api_val = self.entry.options.get(
            "api_key", self.entry.data.get("api_key", "")
        )
        int_val = self.entry.options.get("scan_interval_minuten", 5)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required("api_key", default=str(api_val)): str,
                vol.Required("scan_interval_minuten", default=int(int_val)): int,
            })
        )

class NSReisadviesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NSReisadviesOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Eerste setup."""
        
        # Bestaande entries ophalen via het nieuwe DOMAIN
        existing_entries = self.hass.config_entries.async_entries(DOMAIN)
        
        stored_api_key = None
        for entry in existing_entries:
            if entry.data.get("api_key"):
                stored_api_key = entry.data["api_key"]
                break

        if user_input is not None:
            # Check op dubbelen binnen het nieuwe domein
            for entry in existing_entries:
                existing_act = entry.data.get("act_station", "").lower()
                existing_arr = entry.data.get("arr_station", "").lower()
                new_act = user_input["act_station"].lower()
                new_arr = user_input["arr_station"].lower()

                if existing_act == new_act and existing_arr == new_arr:
                    return self.async_abort(reason="already_configured")

            final_api_key = user_input.get("api_key", stored_api_key)

            return self.async_create_entry(
                title=f"NS {user_input['act_station']} -> {user_input['arr_station']}",
                data={
                    "api_key": final_api_key,
                    "act_station": user_input["act_station"],
                    "arr_station": user_input["arr_station"],
                },
            )

        schema = {}
        if not stored_api_key:
            schema[vol.Required("api_key")] = str
        
        schema[vol.Required("act_station")] = vol.In(STATIONS)
        schema[vol.Required("arr_station")] = vol.In(STATIONS)

        return self.async_show_form(
            step_id="user", 
            data_schema=vol.Schema(schema), 
            errors={}
        )
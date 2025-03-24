import streamlit as st
import folium
from streamlit_folium import folium_static
import requests
from datetime import datetime
import pytz
from deep_translator import GoogleTranslator

# Übersetzer Funktion
def translate(text):
    return GoogleTranslator(source="auto", target="de").translate(text)

# Abruf von RestCountries API
@st.cache_data
def get_country_data(country_code):
    url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[0]
    return None

@st.cache_data
def get_local_time_from_restcountries(country_code):
    url = f"https://restcountries.com/v3.1/alpha/{country_code}"
    response = requests.get(url)

    if response.status_code == 200:
        country_data = response.json()[0]
        timezone = country_data.get('timezones', [None])[0] 
        
        if timezone:
            try:
                country_tz = pytz.timezone(timezone)
                local_time = datetime.now(country_tz).strftime("%H:%M:%S")
                return local_time
            except pytz.UnknownTimeZoneError:
                return "Zeitzone unbekannt"
        else:
            return "Zeitzone nicht verfügbar"
    else:
        return "Daten nicht verfügbar"

# Abruf von Wikidata
# Bilder
def get_image_from_wikidata(wikidata_id):
    sparql_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?image WHERE {{
      wd:{wikidata_id} wdt:P18 ?image.
    }}
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    response = requests.get(sparql_url, params={'query': query, 'format': 'json'}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and 'bindings' in data['results'] and len(data['results']['bindings']) > 0:
            image_url = data['results']['bindings'][0]['image']['value']
            return image_url
    return None

# Bevölkerung
@st.cache_data
def get_population_from_wikidata(wikidata_id):
    sparql_url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?population WHERE {
      wd:""" + wikidata_id + """ wdt:P1082 ?population.
    }
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(sparql_url, params={'query': query, 'format': 'json'}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and 'bindings' in data['results'] and len(data['results']['bindings']) > 0:
            population = data['results']['bindings'][0]['population']['value']
            population_int = int(float(population))
            return f"{population_int:,}".replace(",", ".")
    return "Nicht verfügbar"

# Fläche
@st.cache_data
def get_area_from_wikidata(wikidata_id):
    sparql_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?area WHERE {{
      wd:{wikidata_id} wdt:P2046 ?area.
    }}
    """
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(sparql_url, params={'query': query, 'format': 'json'}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('results', {}).get('bindings'):
            area = float(data['results']['bindings'][0]['area']['value'])
            return f"{area:,.0f}".replace(",", ".")  # Tausenderpunkte für deutsche Schreibweise
    return "Nicht verfügbar"


# Sprache
@st.cache_data
def get_languages_from_wikidata(wikidata_id):
    sparql_url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?languageLabel WHERE {
      wd:""" + wikidata_id + """ wdt:P37 ?language.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],de". }
    }
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    response = requests.get(sparql_url, params={'query': query, 'format': 'json'}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and 'bindings' in data['results'] and len(data['results']['bindings']) > 0:
            languages = [binding['languageLabel']['value'] for binding in data['results']['bindings']]
            return languages
    return ["Nicht verfügbar"]

#Staatsoberhaupt    
@st.cache_data
def get_head_of_state_from_wikidata(wikidata_id):
    sparql_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?headOfState WHERE {{
      wd:{wikidata_id} wdt:P35 ?headOfState.
    }}
    """
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(sparql_url, params={'query': query, 'format': 'json'}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data['results']['bindings']:
            head_of_state_id = data['results']['bindings'][0]['headOfState']['value'].split("/")[-1]
            return get_label_from_wikidata(head_of_state_id)
    
    return "Nicht verfügbar"

@st.cache_data
def get_label_from_wikidata(entity_id, lang="de"):
    """Holt das Label (den Namen) einer Wikidata-Entity (Q-Nummer)."""
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}&props=labels&languages={lang}&format=json"
    response = requests.get(url).json()
    
    labels = response.get("entities", {}).get(entity_id, {}).get("labels", {})
    return labels.get(lang, {}).get("value", "Nicht verfügbar")

#Bürgermeister
@st.cache_data
def get_mayor_from_wikidata(wikidata_id):
    sparql_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?mayorLabel WHERE {{
      wd:{wikidata_id} wdt:P6 ?mayor.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],de". }}
    }}
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(sparql_url, params={'query': query, 'format': 'json'}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and 'bindings' in data['results'] and len(data['results']['bindings']) > 0:
            mayor = data['results']['bindings'][0]['mayorLabel']['value']
            return mayor
    return "Nicht verfügbar"

def get_mayor_value(wikidata_id):
    mayor = get_mayor_from_wikidata(wikidata_id)
    return mayor if mayor else "Nicht verfügbar"

#Währung
def get_currency_from_wikidata(wikidata_id):
    sparql_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?currencyLabel WHERE {{
      wd:{wikidata_id} wdt:P38 ?currency.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],de". }}
    }}
    """    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    response = requests.get(sparql_url, params={'query': query, 'format': 'json'}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and 'bindings' in data['results'] and len(data['results']['bindings']) > 0:
            currency = data['results']['bindings'][0]['currencyLabel']['value']
            return currency
    st.write("Fehler oder keine Währung gefunden", response.json())
    return "Nicht verfügbar"

#Gründungsjahr    
def get_founding_year_from_wikidata(wikidata_id):
    sparql_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?foundingYear WHERE {{
      wd:{wikidata_id} wdt:P571 ?foundingYear.
    }}
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    response = requests.get(sparql_url, params={'query': query, 'format': 'json'}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'results' in data and 'bindings' in data['results'] and len(data['results']['bindings']) > 0:
            founding_year = data['results']['bindings'][0]['foundingYear']['value']
            return founding_year.split("-")[0]
    return "Nicht verfügbar"

#weitere Daten
@st.cache_data
def get_wikidata_info(wikidata_id, info_type, lang="de"):
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={wikidata_id}&sites=en&props=claims&languages={lang}&format=json"
    response = requests.get(url).json()

    claims = response.get("entities", {}).get(wikidata_id, {}).get("claims", {})
    if info_type in claims:
        return claims[info_type][0]["mainsnak"]["datavalue"]["value"]
    return None

# Session state
country = st.session_state["land"]
city = st.session_state["stadt"]
land_id = st.session_state["land_id"]
city_id = st.session_state["city_id"]
city_coord = st.session_state.get("city_coord", None)
land_coord = st.session_state.get("land_coord", None)
alpha3 = st.session_state["alpha3"]  # 'code' wurde in 'alpha3' umbenannt

# API-Daten abrufen
data = get_country_data(alpha3)
local_time = get_local_time_from_restcountries(alpha3)

if data:
    capital = data['capital'][0]
    flag_url = data['flags']['png']
    neighbors = data.get("borders", [])
    timezone = data['timezones'][0]
    
    try:
        country_tz = pytz.timezone(pytz.country_timezones[data['cca2']][0])
        local_time = datetime.now(country_tz).strftime("%H:%M:%S")
    except Exception:
        local_time = "Unbekannt"

# Bedingung zum Abrufen der Daten
if country != "":
    location = city if city != "keine Stadt auswählen" else country

    # Wenn eine Stadt ausgewählt wurde und Koordinaten vorhanden sind, Stadtinformationen anzeigen
    if city != "keine Stadt auswählen" and city_coord:
        st.write(f"### Informationen zur Stadt {city}:")
        col1, col2 = st.columns([2, 3])

        with col1:
            area = get_area_from_wikidata(city_id)
            population = get_population_from_wikidata(city_id)
            mayor = get_mayor_value(city_id)
            currency = get_currency_from_wikidata(land_id)
            founding_year = get_founding_year_from_wikidata(city_id)
            
            st.write(f"####")
            st.write(f"##### Fläche: {area} km²" if area != "Nicht verfügbar" else "Fläche nicht verfügbar")
            st.write(f"##### Einwohner: {population if population else 'Nicht verfügbar'}")
            st.write(f"##### Aktuelle Uhrzeit: {local_time}")
            st.write(f"##### Bürgermeister: {mayor if mayor else 'Nicht verfügbar'}")
            st.write(f"##### Währung: {currency}")
            if founding_year and founding_year != "Nicht verfügbar":
                st.write(f"##### Gründungsjahr: {founding_year}")

        with col2:
            city_image_url = get_image_from_wikidata(city_id)
            
            st.write(f"####")
            st.image(city_image_url, caption=f"Bild von {city}", use_container_width=False, width=400)

        if city_coord:
            city_lat, city_lon = city_coord
            
            st.write(f"#####") 
            st.write("🇦🇱 🇦🇩 🇦🇹 🇧🇾 🇧🇪 🇧🇦 🇧🇬 🇭🇷 🇨🇾 🇨🇿 🇩🇰 🇪🇪 🇫🇮 🇫🇷 🇬🇪 🇩🇪 🇬🇷 🇭🇺 🇮🇸 🇮🇪 🇮🇹 🇽🇰 🇱🇻 🇱🇮 🇱🇹 🇱🇺 🇲🇹 🇲🇩 🇲🇨 🇲🇪 🇳🇱 🇲🇰 🇳🇴 🇵🇱 🇵🇹 🇷🇴 🇷🇺 🇸🇲 🇷🇸 🇸🇰 🇸🇮 🇪🇸 🇸🇪 🇨🇭 🇺🇦 🇬🇧 🇻🇦 ")       
            st.write(f"#### Karte der Stadt {city}")
            karte_stadt = folium.Map(location=[city_lat, city_lon], zoom_start=12, locale="de")
            folium.Marker([city_lat, city_lon], popup=f"{city}").add_to(karte_stadt)
            folium_static(karte_stadt, width=600, height=300)


    # Falls keine Stadt ausgewählt wurde, Landinformationen anzeigen
    else:
        st.write(f"# Willkommen in {country}")
        col1, col2 = st.columns([2, 3])
        
        with col1:
            area = get_area_from_wikidata(land_id)
            population = get_population_from_wikidata(land_id)
            languages = get_languages_from_wikidata(land_id)
            head_of_state = get_head_of_state_from_wikidata(land_id)
            currency = get_currency_from_wikidata(land_id)

            st.write(f"####")
            st.write(f"##### Fläche: {area} km²" if area != "Nicht verfügbar" else "Fläche nicht verfügbar")
            st.write(f"##### Einwohner: {population if population else 'Nicht verfügbar'}")
            st.write(f"##### Hauptstadt: {translate(capital)}")
            st.write(f"##### Sprache(n): {', '.join(languages) if languages else 'Nicht verfügbar'}")
            st.write(f"##### Aktuelle Uhrzeit: {local_time}")
            st.write(f"##### Zeitzone: {country_tz}")
            st.write(f"##### Währung: {currency}")
            st.write(f"##### Staatsoberhaupt: {head_of_state}")
        
        with col2:
            st.write(f"####")
            st.image(flag_url, caption=f"Flagge von {country}", use_container_width=False, width = 400)
            
        # Reisewarnungen
        st.write(f"####")
        st.write("🇦🇱 🇦🇩 🇦🇹 🇧🇾 🇧🇪 🇧🇦 🇧🇬 🇭🇷 🇨🇾 🇨🇿 🇩🇰 🇪🇪 🇫🇮 🇫🇷 🇬🇪 🇩🇪 🇬🇷 🇭🇺 🇮🇸 🇮🇪 🇮🇹 🇽🇰 🇱🇻 🇱🇮 🇱🇹 🇱🇺 🇲🇹 🇲🇩 🇲🇨 🇲🇪 🇳🇱 🇲🇰 🇳🇴 🇵🇱 🇵🇹 🇷🇴 🇷🇺 🇸🇲 🇷🇸 🇸🇰 🇸🇮 🇪🇸 🇸🇪 🇨🇭 🇺🇦 🇬🇧 🇻🇦 ")     
        st.write(f"#### Reisewarnungen des Auswärtigen Amtes:")
        api_url = "https://www.auswaertiges-amt.de/opendata/travelwarning"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if "response" in data:
                warnings = data["response"]
                country_warning = None
                country_id = None
                for key, warning_data in warnings.items():
                    if isinstance(warning_data, dict) and warning_data.get("iso3CountryCode") == alpha3:
                        country_warning = warning_data
                        country_id = key
                        break
                if country_warning:
                    title = country_warning.get("title", "Keine Titel verfügbar")
                    warning = country_warning.get("warning", False)
                    partial_warning = country_warning.get("partialWarning", False)
                    situation_warning = country_warning.get("situationWarning", False)
                    situation_part_warning = country_warning.get("situationPartWarning", False)
                    if any([warning, partial_warning, situation_warning, situation_part_warning]):
                        st.write(f"Es besteht eine Reisewarnung für {country}: {title}")
                        if country_id:
                            url = f"https://www.auswaertiges-amt.de/de/service/laender/{country_id}-sicherheit-{country_id}"
                            st.write(f"Bitte informiere Dich hier: [Reise- und Sicherheitshinweise für {country}]({url})")
                    else:
                        st.write(f"Es gibt keine Reisewarnungen für {country}.")
                else:
                    st.write(f"Keine Reisewarnung für {country} gefunden.")
            else:
                st.error("Fehler: 'response' fehlt in den API-Daten.")
        else:
            st.error(f"Fehler bei der API-Anfrage. Statuscode: {response.status_code}")
        
        # Karte
        #st.write(f"####")
        st.write("🇦🇱 🇦🇩 🇦🇹 🇧🇾 🇧🇪 🇧🇦 🇧🇬 🇭🇷 🇨🇾 🇨🇿 🇩🇰 🇪🇪 🇫🇮 🇫🇷 🇬🇪 🇩🇪 🇬🇷 🇭🇺 🇮🇸 🇮🇪 🇮🇹 🇽🇰 🇱🇻 🇱🇮 🇱🇹 🇱🇺 🇲🇹 🇲🇩 🇲🇨 🇲🇪 🇳🇱 🇲🇰 🇳🇴 🇵🇱 🇵🇹 🇷🇴 🇷🇺 🇸🇲 🇷🇸 🇸🇰 🇸🇮 🇪🇸 🇸🇪 🇨🇭 🇺🇦 🇬🇧 🇻🇦 ")        
        if land_coord:
            lat, lon = land_coord
            st.write("#### Karte des Landes")
            karte = folium.Map(location=[lat, lon], zoom_start=6, locale="de")
            folium.Marker([lat, lon], popup=f"{country}").add_to(karte)
            folium_static(karte, width=700, height=500)
                                                
        # Nachbarländer auflisten
        if neighbors:
            st.write("#### Nachbarländer:")
            full_name_neighbors = []
            for name in neighbors:
                neighbor = get_country_data(name)
                full_name_neighbors.append(translate(neighbor["name"]["common"]))
            st.write(", ".join(full_name_neighbors))
        else:
            st.write("### Nachbarländer: Keine oder keine Daten verfügbar")

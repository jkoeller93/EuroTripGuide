############################################################################
#  Wetter.py
#  mit 
#  API von Openweathermap.org
#  Archive-api.open-meteo.com
############################################################################

import streamlit as st
from meteostat import Stations, Daily
from datetime import datetime, timedelta
import pandas as pd
import requests
import time
import random
import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
#from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY_Open_Weather")

st.sidebar.write(f"**Aktuelle Auswahl:** {st.session_state['land']}" + (f" - {st.session_state['stadt']}" if st.session_state["stadt"] else ""))
st.sidebar.write("")
st.sidebar.markdown("Made with ❤️ by Carolin, Dina, Jonas, Laura")



st.title("🌤️ Wetter in Europa")
st.write("Hier findest Du Infos zu aktuellem Wetter und Wetterprognose in europäischen Ländern/Städten und wetterbedingte Empfehlungen für Deine Reiseziele.")
st.write("")

#@st.cache_data
#def translate(text):
    #return GoogleTranslator(source="auto", target="de").translate(text)


# API-Call-Limiter
MAX_CALLS_PER_DAY = 1000
if "api_calls_today" not in st.session_state:
    st.session_state["api_calls_today"] = 0
@st.cache_data
def can_make_api_call():
    return st.session_state["api_calls_today"] < MAX_CALLS_PER_DAY

@st.cache_data
def increment_api_call():
    if can_make_api_call():
        st.session_state["api_calls_today"] += 1
        time.sleep(1.1)  # Verhindert Überschreitung des 59 Calls/Minute-Limits

# Wetter abrufen
@st.cache_data
def get_weather(city, country_code):
    if not can_make_api_call():
        st.error("Tageslimit für API-Anfragen erreicht! Bitte morgen erneut versuchen.")
        return None

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&units=metric&appid={API_KEY}&lang=de"
    
    try:
        proxies = {"http": None, "https": None}  # Deaktiviert Proxy
        response = requests.get(url, proxies=proxies, timeout=10)  # Setzt Timeout

        if response.status_code == 200:
            increment_api_call()
            return response.json()
        else:
            st.error(f"API-Fehler: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Netzwerkfehler: {e}")
        return None
    # response = requests.get(url)
    # increment_api_call()

    # if response.status_code == 200:
    #     return response.json()
    # return None

# Überprüfung, ob auf Home.py Land und Stadt gewählt wurden
if not st.session_state.get("land") or st.session_state.get("land") == "":
    st.error("🚨 Bitte wähle zuerst ein Land auf der Homepage aus.")
elif not st.session_state.get("stadt") or st.session_state.get("stadt") == "keine Stadt auswählen":
    st.error("🚨 Bitte wähle eine Stadt auf der Homepage aus oder aktiviere die Option 'keine Stadt auswählen'.")
else:
    land = st.session_state["land"]
    stadt = st.session_state["stadt"]
    country_code = st.session_state["alpha3"]

    st.subheader(f"📍 Aktuelles Wetter für {stadt}, {land}")
    st.write("Quelle: API von opentwethermap.org")
    
    weather_data = get_weather(stadt, country_code)

    if weather_data:
        temp = weather_data["main"]["temp"]
        desc = weather_data["weather"][0]["description"]

        # Wetter-Emojis zuordnen
        weather_emojis = {
            "Clear": "☀️",
            "Clouds": "☁️",
            "Rain": "🌧️",
            "Drizzle": "🌦️",
            "Thunderstorm": "⛈️",
            "Snow": "❄️",
            "Mist": "🌫️",
            "Fog": "🌫️",
            "Haze": "🌁",
        }

        emoji = weather_emojis.get(weather_data["weather"][0]["main"], "🌿")

        st.success(f"🌡️ {stadt}: {round(temp, 1)}°C  \n{emoji} {desc.title()}")
    else:
        st.error("❌ Wetterdaten nicht verfügbar.")

################################################################################
st.write("")
st.write("")
st.write("")

#import streamlit as st
#import pandas as pd
#import requests
#import datetime
#import time
#from sklearn.model_selection import train_test_split
#from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
#from sklearn.linear_model import LinearRegression
#from sklearn.metrics import mean_absolute_error


st.subheader("📅 Wetterprognose für Deine Reise")
st.write("Erhalte eine Vorhersage für das Wetter in der Stadt Deiner Wahl aufgrund der historischen Daten (stündliche Werte von den letzten 10 Jahren).  \nVergleiche die berechnete Temperatur mit den tatsächlichen Werten.  \nQuelle: archive-api.open-meteo.com")

# Überprüfung, ob ein Land und eine Stadt auf der Home-Seite ausgewählt wurden
if not st.session_state.get("land") or st.session_state.get("land") == "":
    st.error("🚨 Bitte wähle zuerst ein Land auf der Homepage aus.")
elif not st.session_state.get("stadt") or st.session_state.get("stadt") == "keine Stadt auswählen":
    st.error("🚨 Bitte wähle eine Stadt auf der Homepage aus oder aktiviere die Option 'keine Stadt auswählen'.")
else:
    land = st.session_state["land"]
    stadt = st.session_state["stadt"]
    coordinates = st.session_state.get("city_coord")  # Koordinaten aus Session State
    if not coordinates:
        st.error("🚨 Keine gültigen Koordinaten gefunden. Bitte überprüfe die Stadtwahl.")
    else:
        latitude, longitude = coordinates  # Entpacke Latitude und Longitude

        st.success(f"🌍 Du hast {land} - {stadt} ausgewählt. Wähle jetzt das Datum für die Wetterprognose.")

        # Datumsauswahl
        selected_date = st.date_input("📆 Wähle ein Datum aus:", datetime.date.today() + datetime.timedelta(days=1), min_value=datetime.date.today())

        # Button für Wetterprognose
        if st.button("🔍 Vorhersage berechnen"):
            with st.spinner("📡 Daten werden abgerufen und analysiert... Bitte warten."):
                time.sleep(2)

                # Historische Wetterdaten abrufen
                st.write("📥 Abruf der historischen Wetterdaten...")
                history_url = "https://archive-api.open-meteo.com/v1/archive"
                history_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": "2014-01-01",
                    "end_date": "2025-01-01", #datetime.date.today().strftime("%Y-%m-%d")
                    "hourly": ["temperature_2m", "precipitation"],
                    "timezone": "Europe/Berlin"
                }
                response = requests.get(history_url, params=history_params)
                data = response.json()

                # Umwandlung in DataFrame
                df = pd.DataFrame({
                    "datetime": pd.to_datetime(data["hourly"]["time"]),
                    "temperature": data["hourly"]["temperature_2m"],
                    "precipitation": data["hourly"]["precipitation"]
                })

                # Feature Engineering
                df.set_index("datetime", inplace=True)
                df["hour"] = df.index.hour
                df["day_of_year"] = df.index.dayofyear
                df["month"] = df.index.month

                # Features und Zielvariablen definieren
                X = df[["hour", "day_of_year", "month", "precipitation"]]
                y = df["temperature"]

                # Trainings- und Testdatensatz splitten
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                # Modelle definieren
                models = {
                    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
                    "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
                    "Linear Regression": LinearRegression()
                }

                # Modelle trainieren und evaluieren
                st.write("📊 Modelle werden trainiert und bewertet...")
                results = {}
                for name, model in models.items():
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    mae = mean_absolute_error(y_test, y_pred)
                    results[name] = mae
                    st.write(f"🧠 {name} - Mittlerer absoluter Fehler (mae): {mae:.2f}°C")

                # Bestes Modell auswählen
                best_model_name = min(results, key=results.get)
                best_model = models[best_model_name]
                st.success(f"🏆 Bestes Modell: {best_model_name}")

                # Wettervorhersage für das gewählte Datum
                st.write("📡 Berechnung der Wetterprognose...")
                future_features = pd.DataFrame({
                    "hour": [12],  # Mittag als Referenz
                    "day_of_year": [selected_date.timetuple().tm_yday],
                    "month": [selected_date.month],
                    "precipitation": [0]
                })

                future_prediction = best_model.predict(future_features)
                predicted_temp = round(future_prediction[0], 2)

                st.success(f"🔮 Vorhergesagte Temperatur für {stadt} am {selected_date}: **{predicted_temp}°C**")

                # Tatsächliche Temperatur abrufen und Vergleich
                st.write("📡 Abruf der tatsächlichen Temperatur zum Vergleich...")
                actual_url = "https://api.open-meteo.com/v1/forecast"
                actual_params = {
                    "latitude": latitude,
                    "longitude": longitude,
                    "hourly": ["temperature_2m"],
                    "timezone": "Europe/Berlin",
                    "start_date": selected_date.strftime("%Y-%m-%d"),
                    "end_date": selected_date.strftime("%Y-%m-%d")
                }
                actual_response = requests.get(actual_url, params=actual_params)
                actual_data = actual_response.json()

                if "hourly" in actual_data and "temperature_2m" in actual_data["hourly"]:
                    actual_temperature = actual_data["hourly"]["temperature_2m"][12]
                    error = abs(actual_temperature - predicted_temp)

                    st.success(f"🌡️ Tatsächliche Temperatur von api.open-meteo.com am {selected_date}: **{actual_temperature:.2f}°C**")
                    st.write(f"📊 **Fehlerunterschied der Vorhersage:** {error:.2f}°C")
                else:
                    st.warning("⚠️ Tatsächliche Temperaturdaten sind noch nicht verfügbar.")



################################################################################

# Temperaturfilter für Empfehlungen
    st.write("")
    st.write("")
    st.write("")

    BASE_URL = "http://api.openweathermap.org/data/2.5/group"

    # Liste mit europäischen Städten und OpenWeather City-IDs
    city_ids_dict = {
        "Berlin": 2950159, "Hamburg": 2911298, "München": 2867714,
        "Madrid": 3117735, "Barcelona": 3128760, "Valencia": 2509954,
        "Paris": 2988507, "Marseille": 2995469, "Lyon": 2996944,
        "Rome": 3169070, "Milan": 3173435, "Neapel": 3172394,
        "Stockholm": 2673730, "Gothenburg": 2711537, "Malmo": 2692969,
        "Lisbon": 2267057, "Porto": 2735943, "Braga": 2742032,
        "Athens": 264371, "Thessaloniki": 734077, "Patras": 255683,
        "Vienna": 2761369, "Salzburg": 2766824, "Innsbruck": 2775220,
        "Oslo": 3143244, "Bergen": 3161732, "Trondheim": 3133880,
        "London": 2643743, "Manchester": 2643123, "Birmingham": 2655603,
        "Dublin": 2964574, "Cork": 2965140, "Galway": 2964180,
        "Brussels": 2800866, "Antwerpen": 2803138, "Ghent": 2797656,
        "Amsterdam": 2759794, "Rotterdam": 2747891, "Den Haag": 2747373,
        "Copenhagen": 2618425, "Aarhus": 2624652, "Odense": 2615876,
        "Helsinki": 658225, "Espoo": 660158, "Tampere": 634963,
        "Warschau": 756135, "Krakow": 3094802, "Wroclaw": 3081368,
        "Prag": 3067696, "Brno": 3078610, "Ostrava": 3068799,
        "Budapest": 3054643, "Debrecen": 3052009, "Szeged": 3046526,
        "Bratislava": 3060972, "Kosice": 723819,
        "Ljubljana": 3196359, "Maribor": 3197559,
        "Zagreb": 3186886, "Split": 3190261, "Rijeka": 3191648,
        "Sarajevo": 3191281, "Banja Luka": 3204541,
        "Belgrad": 792680, "Novi Sad": 3194360, "Niš": 787657,
        "Podgorica": 3193044,
        "Tirana": 3183875, "Durrës": 3185728,
        "Skopje": 785842, "Bitola": 792578,
        "Sofia": 727011, "Plovdiv": 728193, "Varna": 726050,
        "Bucharest": 683506, "Cluj-Napoca": 681290, "Timișoara": 665087,
        "Chisinau": 618426, "Tiraspol": 617239,
        "Kiev": 703448, "Kharkiv": 706483, "Odessa": 698740,
        "Minsk": 625144, "Homel": 627907,
        "Moskau": 524901, "Sankt Petersburg": 498817, "Nowosibirsk": 1496747,
        "Ankara": 323784, "Istanbul": 745044, "Izmir": 311046,
        "Andorra la Vella": 3041566, "Vaduz": 3042030, "Luxembourg": 2960316,
        "Tallinn": 588409, "Vilnius": 593116, "Riga": 456173,
        "Reykjavik": 3413829, "Valletta": 2562305, 
        "Bern": 2661552, "Zürich": 2657896, "Genf": 2660646,
        "Nicosia": 146268

    }

    city_ids = list(city_ids_dict.values())

    # Funktion zum Abrufen der Wetterdaten (max. 20 Städte pro API-Call)
    @st.cache_data
    def get_weather_data(city_ids):
        weather_data = []
        proxies = {"http": None, "https": None}  # Proxy deaktivieren (Carolin eingefügt)

        for i in range(0, len(city_ids), 20):
            city_chunk = city_ids[i:i + 20]
            city_id_str = ",".join(map(str, city_chunk))

            url = f"{BASE_URL}?id={city_id_str}&units=metric&appid={API_KEY}"

            try:
                response = requests.get(url, proxies=proxies, timeout=10)  # Timeout hinzufügen
                if response.status_code == 200:
                    data = response.json()
                    weather_data.extend(data["list"])
                else:
                    st.error(f"⚠️ Fehler beim Abruf der Wetterdaten ({response.status_code})")
    
                time.sleep(1)  # API-Limit einhalten
    
            except requests.exceptions.RequestException as e:
                st.error(f"Netzwerkfehler: {e}")
                return []
                
                
            # response = requests.get(url)

            # if response.status_code == 200:
                # data = response.json()
                # weather_data.extend(data["list"])
            # else:
                # st.error(f"⚠️ Fehler beim Abruf der Wetterdaten ({response.status_code})")

            # time.sleep(1)  # Vermeidung von API-Limits

        return weather_data

    # UI in Streamlit
    st.subheader("🌄 Städteempfehlungen nach Temperatur")
    st.info("Finde europäische Städte mit Deiner Wunschtemperatur.")

    # Temperaturbereich auswählen
    min_temp, max_temp = st.slider("🌡️ Wähle eine Temperaturspanne aus:", -20, 40, (0, 5))

    # Button für API-Abruf
    if st.button("🔍 Städte finden"):
        weather_info = get_weather_data(city_ids)

        if weather_info:
            # Städte nach Temperatur filtern
            matching_cities = [
                (city["name"], round(city["main"]["temp"], 1))
                for city in weather_info if min_temp <= city["main"]["temp"] <= max_temp
            ]

            # Falls keine Städte gefunden wurden
            if not matching_cities:
                st.warning("❌ Keine Städte mit dieser Temperaturspanne gefunden.")
            else:
                # Städte aufsteigend nach Temperatur sortieren
                matching_cities.sort(key=lambda x: x[1])

                # Maximal 5 Städte anzeigen               
                st.info("Top 5 für Dich empfohlene Städte:")
                selected_cities = matching_cities[:3] + matching_cities[-2:]

                for city, temp in selected_cities:
                    st.write(f"🌡️ {city}: {round(temp, 1)}°C")

        else:
            st.error("⚠️ Fehler beim Abruf der Wetterdaten.")

################################################################################

# Die wärmsten & kältesten Städte Europas  
st.write("")
st.write("")
st.write("")


# API-Call mit Batch-Request (maximal 20 Städte pro Abruf)
@st.cache_data
def get_weather_data(city_ids):
    """Holt Wetterdaten für eine Gruppe von Städten in einem API-Call."""
    city_id_list = ",".join(map(str, city_ids))
    url = f"http://api.openweathermap.org/data/2.5/group?id={city_id_list}&units=metric&appid={API_KEY}"

    try:
        proxies = {"http": None, "https": None}  # Proxy deaktivieren (Carolin eingefügt)
        response = requests.get(url, proxies=proxies)
        
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Fehler beim Abrufen der Wetterdaten: {e}")
        
    return None

def get_hot_and_cold_cities():
    """Findet die heißesten und kältesten Städte in Europa basierend auf API-Daten."""
    sampled_cities = random.sample(list(city_ids_dict.values()), min(20, len(city_ids_dict)))  # Max. 20 Städte prüfen
        
    # API-Anfragen in Batches von max. 20 Städten
    batch_size = 20
    weather_data = []
        
    for i in range(0, len(sampled_cities), batch_size):
        city_chunk = sampled_cities[i:i + batch_size]
        data = get_weather_data(city_chunk)
            
        if data:
            for city in data["list"]:
                weather_data.append((city["name"], round(city["main"]["temp"], 1)))  # Auf eine Nachkommastelle runden
            
        time.sleep(1)  # Wartezeit, um API-Limit nicht zu überschreiten
        
    # Falls keine gültigen Daten vorhanden sind
    if len(weather_data) < 5:
        st.warning("Nicht genügend Wetterdaten verfügbar.")
        return [], []

    # Nach Temperatur sortieren
    weather_data.sort(key=lambda x: x[1], reverse=True)
        
    # 5 heißeste & 5 kälteste Städte sortiert
    return weather_data[:5], weather_data[-5:]

# Streamlit UI
st.subheader("🔥 Die wärmsten und kältesten Städte Europas heute ❄️")

# Session State für Wetterdaten speichern
if "weather_data" not in st.session_state:
    st.session_state["weather_data"] = None

# Button für Abruf der Städte
st.write("")
if st.button("🎯 Top 5 Städte abrufen"):
    st.session_state["weather_data"] = get_hot_and_cold_cities()

# Falls Daten bereits abgerufen wurden, anzeigen
if st.session_state["weather_data"]:
    hot_cities, cold_cities = st.session_state["weather_data"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔥 Wärmste Städte:**")
        for city, temp in hot_cities:
            st.write(f"☀️ {city}: {round(temp, 1)}°C")

    with col2:
        st.markdown("**❄️ Kälteste Städte:**")
        for city, temp in cold_cities:
            st.write(f"⛷️ {city}: {round(temp, 1)}°C")

################################################################################


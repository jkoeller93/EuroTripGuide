import requests
import streamlit as st
import datetime
import sys
from deep_translator import GoogleTranslator
import folium
from streamlit_folium import folium_static
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY_Ticketmaster")

# Dokumentation Ticketmaster-API: https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/#search-events-v2

# Den übergeordneten Ordner zum sys.path hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from countries_and_cities import countries_and_cities

city = st.session_state["stadt"]
land = st.session_state["land"]
city_en = GoogleTranslator(source='de', target='en').translate(city)

st.sidebar.write(f"**Aktuelle Auswahl:** {st.session_state['land']}" + (f" - {st.session_state['stadt']}" if st.session_state["stadt"] else ""))
st.sidebar.markdown("Made with ❤️ by Dina, Jonas, Laura, Carolin")

if "event_infos" not in st.session_state:
    st.session_state["event_infos"] = {"name": [], "lat": [], "lon": [], "date": [], "time": []}

event_infos = st.session_state["event_infos"]  # Stets aus Session State abrufen

# Einleitung
st.title(f"Veranstaltungen in {city}")
st.write(f"Hier stellen wir dir Informationen über Veranstaltungen in {city} zusammen")
st.header("Für welchen Zeitraum möchtest du suchen?")

date_start = st.date_input("Wähle ein Startdatum aus:", value=datetime.date.today())
date_end = st.date_input("Wähle ein Enddatum aus:")
button = st.button(f"Zeige Veranstaltungen im Zeitraum von {date_start} bis {date_end}")

# URL für die Ticketmaster Discovery API
url = "https://app.ticketmaster.com/discovery/v2/events.json"

# Anfrageparameter
params = {
    "apikey": API_KEY,  # API-Schlüssel
    "city": city_en,  # Stadt
    "startDateTime": f"{date_start}T00:00:00Z",  # Startdatum
    "endDateTime": f"{date_end}T23:59:59Z",  # Enddatum
    "size": 200
}

if button:
    # Anfrage an die Ticketmaster API
    response = requests.get(url, params=params)

    # Prüfen ob event_infos besteht und löschen, falls ja
    if event_infos:
        for key in event_infos:
            event_infos[key].clear()
        print(event_infos)

    col_1, col_2 = st.columns([4,2])

    # Prüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        data = response.json()

        # Überprüfen, ob Events vorhanden sind
        if "_embedded" in data and "events" in data["_embedded"]:
            events = data["_embedded"]["events"]
            count_events = len(data["_embedded"]["events"])
            # Button direkt über den Events platzieren
            if count_events > 0:
                col_2.markdown('<a href="#map-section" style="text-decoration: none;">'
                            '<button style="background-color:#4CAF50; color:white; padding:10px 20px; '
                            'border:none; cursor:pointer; font-size:16px; margin-bottom: 20px;">Klicke HIER für eine Karte mit allen Veranstaltungen</button></a>',
                            unsafe_allow_html=True)
            # Alle Events in der Stadt Berlin ausgeben
            if count_events == 1:
                col_1.write(f"Es wurde {count_events} Event in {city} gefunden:\n")
            else:
                col_1.write(f"Es wurden {count_events} Events in {city} gefunden:\n")

            for event in events:
                event_name = event.get("name", "unbekannt")
                event_infos["name"].append(event_name)
                event_url = event.get("url", "Keine URL verfügbar")
                event_image = event["images"][0].get("url", "unbekannt")
                with col_2:
                    st.markdown(f"""
                        <style>
                            .custom-image {{
                                height: 200px;
                                width: auto;
                            }}
                        </style>
                        <img src="{event_image}" class="custom-image">
                    """, unsafe_allow_html=True)
                    st.markdown("<br><br>", unsafe_allow_html=True)
                col_1.subheader(event_name)
                # Prüfen, ob Zeitangaben vorliegen
                if "dates" in event and "start" in event["dates"]:
                    event_date = event["dates"]["start"].get("localDate", "unbekannt")
                    event_infos["date"].append(event_date)
                    event_date_obj = datetime.datetime.strptime(event_date, "%Y-%m-%d")
                    weekday = event_date_obj.strftime("%A")
                    event_time = event["dates"]["start"].get("localTime", "unbekannt")
                    event_infos["time"].append(event_time)
                    event_timezone = event["dates"].get("timezone", "unbekannt")
                    col_1.write(f" 📅 Datum: {weekday}, {event_date}, Uhrzeit: {event_time}, Zeitzone: {event_timezone}")
                # Prüfen, ob Informationen zum Segment und Genre vorliegen
                if "classifications" in event and "segment" in event["classifications"][0] and "genre" in event["classifications"][0]:
                    event_segment = event["classifications"][0]["segment"].get("name", "unbekannt")
                    event_genre = event["classifications"][0]["genre"].get("name", "unbekannt")
                    col_1.write(f" 🎭 Segment: {event_segment}, Genre: {event_genre}")
                # Prüfen, ob Informationen zum Preis vorliegen
                if "priceRanges" in event:
                    price_min = event["priceRanges"][0].get("min", 0)
                    price_max = event["priceRanges"][0].get("max", 0)
                    currency = event["priceRanges"][0].get("currency", "unbekannt")
                    if price_min and price_max != 0:
                        if price_min == price_max:
                            col_1.write(f" 💰 Preis: {int(price_min)} {currency}")
                        else:
                            col_1.write(f" 💰 Preis: {int(price_min)} - {int(price_max)} {currency}")
                    else:
                        col_1.write(f" 💰 Preis: unbekannt")
                # Prüfen, ob Informationen zum Segment und Genre vorliegen
                if "_embedded" in event and "venues" in event["_embedded"]:
                    event_venue = event["_embedded"]["venues"][0].get("name", "Unbekannt")
                    # Prüfen, ob Informationen zum Ort vorliegen
                    if "address" in event["_embedded"]["venues"][0]:
                        event_address = event["_embedded"]["venues"][0]["address"].get("line1", "Unbekannt")
                        col_1.write(f" 📍  Veranstaltungsort: {event_venue}, Adresse: {event_address}")
                        col_1.markdown(f" Weitere Infos: [Klicke HIER für weitere Informationen zur Veranstaltung]({event_url})")
                    # Prüfen, ob Informationen zum Schauspieler vorliegen
                    if "attractions" in event["_embedded"]:
                        event_artist_name = event["_embedded"]["attractions"][0].get("name", "unbekannt")
                    # Prüfen, ob Informationen zu den Koordinaten vorliegen
                    if "location" in event["_embedded"]["venues"][0]:
                        event_longitude = event["_embedded"]["venues"][0]["location"].get("longitude", None)
                        event_latitude = event["_embedded"]["venues"][0]["location"].get("latitude", None)
                        if event_longitude and event_latitude:
                            try:
                                # Leere Strings durch Standardwerte ersetzen, wenn nötig
                                event_latitude = event_latitude.strip() if event_latitude.strip() != "" else "0.0"
                                event_longitude = event_longitude.strip() if event_longitude.strip() != "" else "0.0"

                                # Wenn ein Komma als Dezimaltrennzeichen verwendet wird, ersetze es durch einen Punkt
                                event_latitude = event_latitude.replace(",", ".")
                                event_longitude = event_longitude.replace(",", ".")

                                # Umwandeln der Koordinaten in float
                                lat, lon = float(event_latitude), float(event_longitude)
                                event_infos["lat"].append(lat)
                                event_infos["lon"].append(lon)

                                # Ausgabe der umgewandelten Koordinaten
                            except ValueError as e:
                                print(f"Fehler beim Umwandeln der Koordinaten: {e}")

        else:
            st.write(f"Leider keine Events in {city} im Zeitraum von {date_start} bis {date_end} gefunden.")
            st.write(f"Vielleicht findest du ja Veranstaltungen in einer anderen Stadt")
            other_cities = [city[0] for city in countries_and_cities[land]["cities"] if city[0] != city]
            st.selectbox(f"Gehe zurück und wähle eine andere Stadt in {land} aus", other_cities)
    else:
        st.write(f"Fehler bei der Anfrage: {response.status_code}")

    # Anker für die Karte setzen
    st.markdown('<div id="map-section"></div>', unsafe_allow_html=True)

    if "lat" in event_infos and "lon" in event_infos and event_infos["lat"] and event_infos["lon"]:
        # Mittelpunkt auf den ersten Event setzen
        map_center = (event_infos["lat"][0], event_infos["lon"][0])
        karte = folium.Map(location=map_center, zoom_start=12)

        # Füge alle Event-Standorte als Marker hinzu
        for i in range(len(event_infos["name"])):
            folium.Marker(
                location=[event_infos["lat"][i], event_infos["lon"][i]],
                popup=f"{event_infos["name"][i]}\n{event_infos["date"][i]}, {event_infos["time"][i]}",  # Name als Popup
                icon=folium.Icon(color="blue", icon="info-sign")  # Optional: Icon anpassen
            ).add_to(karte)

        # Zeige die Karte in Streamlit
        st.subheader(f"Dies ist eine interaktive Karte mit allen Veranstaltungen in {city}\nDu kannst die Karte verschieben, zoomen oder auf die jeweilige Veranstaltung klicken, um mehr Infos zu erhalten")
        folium_static(karte, width=1000, height=600)

        # Button zum Zurück zum Anfang der Seite
        if st.button("Zurück zum Anfang"):
            st.markdown("""
                <script>
                    window.scrollTo(0, 0);
                </script>
            """, unsafe_allow_html=True)

    else:
        st.write("")

############################################################################
#  Feiertage.py
#  mit 
#  Holidays-Modul Python-Bibliothek
#  API von calendarific.com
############################################################################

import streamlit as st
import requests
import datetime
import time
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY_Calendarific")

st.sidebar.write(f"**Aktuelle Auswahl:** {st.session_state['land']}" + (f" - {st.session_state['stadt']}" if st.session_state["stadt"] else ""))
st.sidebar.write("")
st.sidebar.markdown("Made with ❤️ by Carolin, Dina, Jonas, Laura")

# Eigene Länderliste mit Alpha-2-Codes
COUNTRIES = {
    "Deutschland": "DE",
    "Albanien": "AL",
    "Andorra": "AD",
    "Armenien": "AR",
    "Aserbaidschan": "AZ",
    "Belgien": "BE",
    "Bosnien und Herzegowina": "BA",
    "Bulgarien": "BG",
    "Dänemark": "DK",
    "Estland": "EE",
    "Finnland": "FI",
    "Frankreich": "FR",
    "Georgien": "GE",
    "Griechenland": "GR",
    "Großbritannien": "GB",
    "Irland": "IE",
    "Italien": "IT",
    "Island": "IS",
    "Kosovo": "XK",
    "Kroatien": "HR",
    "Lettland": "LV",
    "Liechtenstein": "LI",
    "Litauen": "LT",
    "Luxemburg": "LU",
    "Malta": "MT",
    "Moldawien": "MD",
    "Monaco": "MC",
    "Montenegro": "ME",
    "Niederlande": "NL",
    "Nordmazedonien": "MK",
    "Norwegen": "NO",
    "Österreich": "AT",
    "Polen": "PL",
    "Portugal": "PT",
    "Rumänien": "RO",
    "Russland": "RU",
    "San Marino": "SM",
    "Schweden": "SE",
    "Schweiz": "CH",
    "Serbien": "RS",  
    "Slowakei": "SK",
    "Slowenien": "SI",
    "Spanien": "ES",
    "Tschechien": "CZ",
    "Türkei": "TR",
    "Ungarn": "HU",
    "Weißrussland": "BY",
    "Zypern": "CY"
    
}

# Liste großer Feiertage, die Reisekosten beeinflussen können
#BIG_HOLIDAYS = ["Weihnachten", "Ostern", "Silvester", "Neujahr", "Pfingsten"]

# Caching-Funktion für Übersetzungen
@st.cache_data
def translate(text):
    return GoogleTranslator(source="auto", target="de").translate(text)

# Caching für API-Daten (1 Monat speichern)
@st.cache_data(ttl=30 * 24 * 60 * 60)  # 30 Tage Cache
def get_holidays_cached(country_code, year):
    return get_holidays(country_code, year)

# API-Aufrufe begrenzen (Zählt pro Session)
if "api_calls" not in st.session_state:
    st.session_state.api_calls = 0

# Funktion zum Abrufen der Feiertage über Calendarific API
@st.cache_data
def get_holidays(country_code, year):
    if st.session_state.api_calls >= 500:
        return None, "⚠️ Monatslimit von 500 API-Aufrufen erreicht! Warte bis nächsten Monat."

    url = f"https://calendarific.com/api/v2/holidays?api_key={API_KEY}&country={country_code}&year={year}"
    response = requests.get(url)

    # Falls API-Limit überschritten, kurz warten und erneut versuchen
    if response.status_code == 429:
        time.sleep(2)
        response = requests.get(url)

    if response.status_code != 200:
        return None, "❌ Fehler beim Abrufen der API-Daten."

    data = response.json()

    if "response" not in data or "holidays" not in data["response"]:
        return None, "⚠️ Keine Feiertage gefunden."

    holidays = []
    for holiday in data["response"]["holidays"]:
        name = holiday.get("name", "Unbekannter Feiertag")
        description = holiday.get("description", "Keine Beschreibung verfügbar.")
        date = holiday["date"]["iso"]

        holidays.append({
            "name": translate(name),
            "date": date,
            "description": translate(description),
        })

    st.session_state.api_calls += 1
    return holidays, None

# 🎉 Streamlit UI für Feiertage
st.title(f"🎉 Feiertage in {st.session_state["land"]}")
st.write("Hier findest du Informationen zu nationalen, regionalen, religiösen und inoffiziellen Feiertagen im ausgewählten europäischen Land.  \nQuelle: API calendarific.com")
st.write("")
st.write("")

# Überprüfen, ob ein Land aus `Home.py` gewählt wurde
if "land" in st.session_state and st.session_state["land"]:
    country_name = st.session_state["land"]

    # Umwandlung in Alpha-2-Code
    if country_name in COUNTRIES:
        country_code = COUNTRIES[country_name]
    else:
        st.error("⚠️ Das gewählte Land ist nicht in der Liste enthalten!")
        st.stop()

    # Jahr wählen
    year = st.number_input("📅 Wähle ein Jahr aus, um aktuelle/bewegliche Feiertage abzurufen (Verfügbar von 2000 bis 2050):", min_value=2000, max_value=2050, value=datetime.datetime.now().year, step=1)

    # Button für API-Abfrage
    if st.button(f"🔍 Feiertage in {country_name} anzeigen"):
        holidays, error = get_holidays_cached(country_code, year)

        if error:
            st.warning(error)
        elif holidays:
            st.success(f"📌 {len(holidays)} Feiertage gefunden!")
            for holiday in holidays:
                st.subheader(f"🎉 {holiday['name']} ({holiday['date']})")
                st.write(holiday["description"])

                # Warnung für große Feiertage
                #if any(h in holiday["name"] for h in BIG_HOLIDAYS):
                    #st.warning(f"⚠️ Achtung! Am **{holiday['name']}** können Reisekosten steigen. Flughäfen, Hotels und Verkehr sind oft teurer oder überfüllt. Geschäfte und Läden sind geschlossen oder haben eingeschränkte Öffnungszeiten.")
        else:
            st.warning("⚠️ Keine Feiertage gefunden.")
else:
    st.warning("Bitte wähle zuerst ein Land auf der Homepage aus und klicke **Los geht's** an!")

###############################################################################
st.write("")
st.write("")
st.write("")
st.write("🎉 🎈 🎆 🎇 🎂 🎁 🏵️ 🎃 👻 🎄 🎅 🤶 🦌 ⛄ ❄️ 🔔 🕯️ 🐰 🥚 🐥 🌸 💘 💌 🌹 💑 🎭 🎊 🎉 🤹 🎺 🥂 🎊 🎈 🎁 🏵️ 🎄 🎅 🐥 🌸")
st.write("")
st.write("")

import holidays

# Übersetzer 
@st.cache_data
def translate(text):
    return GoogleTranslator(source="auto", target="de").translate(text)

# Streamlit-Seite für Feiertage
def feiertage():
            
    # Liste der unterstützten europäischen Länder
    european_countries = COUNTRIES
    
    german_speaking_countries = {"Deutschland": "DE", "Schweiz": "CH", "Österreich": "AT", "Luxemburg": "LU", "Liechtenstein": "LI"}

    # Große Feiertage, die Reiseauswirkungen haben können
    big_holidays = ["Weihnachten", "Weihnachtstag", "Erster Weihnachtstag", "Zweiter Weihnachtstag","Heiligabend", "Natale", "Silvester", "Noël", "Ostern", "Ostersonntag", "Ostermontag", "Neujahr", "Pfingsten", "Pfingstmontag"]


# Feiertage-Bereich
        
    st.header("📅 Feiertags-Checker für Reisen")
    st.write("Prüfe hier, ob während Deiner Reise große gesetzliche Feiertage anstehen, und erhalte rechtzeitig hilfreiche Hinweise.")

    st.write("")
    st.write("")

    # Benutzer wählt ein Land aus
    country = st.selectbox("📍 Wähle ein Land aus:", list(european_countries.keys()))

    # Benutzer gibt Zeitraum ein
    start_date = st.date_input("📅 Startdatum", datetime.date.today())
    end_date = st.date_input("📅 Enddatum", datetime.date.today() + datetime.timedelta(days=30))

    # Falls Startdatum nach Enddatum liegt, Fehler anzeigen
    if start_date > end_date:
        st.error("🚨 Das Startdatum darf nicht nach dem Enddatum liegen!")

    else:
        # Feiertage abrufen
        country_code = european_countries[country]
        country_holidays = holidays.country_holidays(country_code, years=range(start_date.year, end_date.year + 1))

        # Feiertage im gewählten Zeitraum filtern
        filtered_holidays = {date: name for date, name in country_holidays.items() if start_date <= date <= end_date}

        if filtered_holidays:
            st.success(f"🎉 Es gibt **{len(filtered_holidays)} Feiertage** im gewählten Zeitraum.  \n📌 Beachte, dass an Feiertagen landesweit Geschäfte, Läden und Dienstleistungen geschlossen sein oder eingeschränkte Öffnungszeiten haben können. Plane Deine Reise entsprechend, um Überraschungen zu vermeiden.")

                
            for date, name in filtered_holidays.items():

                if country in german_speaking_countries:
                    translated_name = name  # Keine Übersetzung für deutschsprachige Länder
                else:
                    translated_name = translate(name)

                st.write(f"- **{date}**: {name} - {translated_name}")

                # Warnung bei großen Feiertagen
                if any(holiday in translate(name) for holiday in big_holidays):
                        st.warning(f"⚠️ Achtung! Am **{name}** können Reisekosten steigen und Verzögerungen auftreten. Flugpreise, Hotels und Verkehr sind oft teurer oder überfüllt.")

        else:
            st.info("✅ In Deinem geplanten Reisezeitraum gibt es **keine offiziellen Feiertage**. Du kannst Deine Reise ungestört genießen! 🎊")    
    

if __name__ == "__main__":
       feiertage()

st.write("")
st.write("")
st.write("Viel Spaß bei der Planung Deiner Reise! 🚀")

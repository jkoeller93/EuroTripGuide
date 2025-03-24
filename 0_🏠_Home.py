import streamlit as st
from deep_translator import GoogleTranslator
from countries_and_cities import countries_and_cities


st.set_page_config(
    page_title = "EuroTripGuide",
    page_icon = "🌍", 
    layout = "wide"
)

# Übersetzer initialisieren
@st.cache_data
def translate(text):
    return GoogleTranslator(source="auto", target="de").translate(text)

# Koordinaten der Städte bekommen
@st.cache_data
def get_city_coordinates(country, city_name):
    for city in countries_and_cities.get(country, {}).get('cities', []):
        if city[0] == city_name:
            return city[2]  # Koordinaten zurückgeben
    return None  # Falls Stadt nicht gefunden wird
    
# Koordinaten des Landes bekommen
@st.cache_data
def get_land_coordinates(country):
    if country in countries_and_cities:
        return countries_and_cities[country].get('coordinates', None)  # Koordinaten des Landes zurückgeben
    return None  # Falls Land nicht gefunden wird

# Arbeitstitel. nicht final
st.title('🗺️ EuroTripGuide 🗺️')
st.header('Deine multifunktionale Reise-App für Städte, Länder, Kultur und Wetterinfos in Europa')

# Einführungstext
st.write("🚂 🚲 🚌 🛶 🗺️ ⛺️ 🏔️ ⛵️ ✈️ 🚂 🚲 🚌 🛶 🗺️ ⛺️ 🏔️ ⛵️ ✈️ 🚂 🚲 🚌 🛶 🗺️ ⛺️ 🏔️ ⛵️ ✈️ 🚂 🚲 🚌 🛶 🗺️ ⛺️ 🏔️ ⛵️ ✈️ 🚂 🚲 🚌 🛶 🗺️ ⛺️ 🏔️ ⛵️ ✈️ ")
st.write("")
st.write("Europa wartet auf dich! Mit EuroTripGuide hast du alle Infos, die du brauchst, um deine Reise zu planen und das Beste aus deinem Abenteuer herauszuholen. Entdecke faszinierende Städte, erfahre mehr über die Gesellschaft und bleibe mit aktuellen Wetter- und Event-Infos immer up to date. Dein perfekter Reisebegleiter für ganz Europa!")
st.write("")
st.write("Über welches Land möchtest Du dich informieren?")

# Session State initialisieren
if "land" not in st.session_state:
    st.session_state["land"] = ""
if "stadt" not in st.session_state:
    st.session_state["stadt"] = ""
if "alpha3" not in st.session_state:
    st.session_state["alpha3"] = ""
if "city_coord" not in st.session_state:
    st.session_state["city_coord"] = ""
if "land_id" not in st.session_state:
    st.session_state["land_id"] = ""
if "city_id" not in st.session_state:
    st.session_state["city_id"] = ""
if "land_coord" not in st.session_state:
    st.session_state["land_coord"] = ""
if "button" not in st.session_state:
    st.session_state["button"] = False


# Auswahl für Land in einer Variable definieren
land = st.selectbox("Wähle ein Land aus", list(countries_and_cities.keys()))

# Liste der Städte in ausgewähltem land anlegen
städte =[city[0] for city in countries_and_cities[land]['cities']]

# Auswahl der Städte des ausgewählten Landes definieren
stadt = st.selectbox("Wähle eine Stadt aus (optional)", ["keine Stadt auswählen"]+ städte)



# Auswahl mit Button bestätigen
button = st.button("los geht's")

# st.session_state["button"] = button

if button:
    st.session_state["land"] = land
    st.session_state["alpha3"] = countries_and_cities[land]['iso_alpha_3']
    st.session_state["stadt"] = stadt
    st.session_state["city_coord"] = get_city_coordinates(land, stadt)
    st.session_state["land_coord"] = get_land_coordinates(land)
    st.session_state["land_id"] = countries_and_cities[land]['country_id']
    st.session_state["button"] = not st.session_state["button"] 
    if stadt != "keine Stadt auswählen":
        # Stadt aus der Liste der Städte im Dictionary suchen
        for city in countries_and_cities[land]['cities']:
            if city[0] == stadt:
                st.session_state["city_id"] = city[1]
                break
                
    if stadt == "keine Stadt auswählen":
        st.write("Du hast",  st.session_state["land"] , "und keine Stadt ausgewählt. Lass uns mal schauen, was wir finden können!")

    elif stadt != "keine Stadt auswählen":
        st.write("Du hast", st.session_state["stadt"], "in",  st.session_state["land"] , "ausgewählt. Lass uns mal schauen, was wir finden können!")
        
st.write("")
st.write("")
st.write("Dir werden größere Städte mit mehr als 100.000 Einwohnern angezeigt. Manchmal gibt es zu einer Stadt keine detaillieten Informationenen. Dann bekommst Du Infos zum Land.")
st.write("Viel Spaß!")

# Anzeige der aktuellen Auswahl
st.sidebar.write(f"**Aktuelle Auswahl:** {st.session_state['land']}" + (f" - {st.session_state['stadt']}" if st.session_state["stadt"] else ""))
st.sidebar.write("")
st.sidebar.markdown("Made with ❤️ by  Carolin, Dina, Jonas, Laura")

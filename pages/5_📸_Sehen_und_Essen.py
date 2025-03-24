import streamlit as st
import requests
import json
import folium
from streamlit_folium import folium_static
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_PLACES_API_KEY = os.getenv("API_KEY_Google_Places")

st.sidebar.write(f"**Aktuelle Auswahl:** {st.session_state['land']}" + (f" - {st.session_state['stadt']}" if st.session_state["stadt"] else ""))
st.sidebar.write("")
st.sidebar.markdown("Made with ❤️ by Dina, Jonas, Laura, Carolin")

# Funktion zum Abrufen der Top-5 Sehenswürdigkeiten
def get_top_attractions(location):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=top+attractions+in+{location}&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    attractions = []
    for place in data.get("results", [])[:6]:  # Nur die ersten 5
        name = place.get("name", "Keine Info")
        desc = place.get("formatted_address", "Keine Adresse verfügbar")
        photo_reference = place.get("photos", [{}])[0].get("photo_reference")
        image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={GOOGLE_PLACES_API_KEY}" if photo_reference else None
        
        attractions.append((name, desc, image_url))
    
    return attractions

def get_best_restaurants(location):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=best+restaurants+in+{location}&key={GOOGLE_PLACES_API_KEY}"
    response = requests.get(url)
    data = response.json()
    restaurants = []
    for place in data.get("results", [])[:10]:
        name = place.get("name", "Keine Info")
        address = place.get("formatted_address", "Keine Adresse verfügbar")
        rating = place.get("rating")
        lat = place.get("geometry", {}).get("location", {}).get("lat")
        lng = place.get("geometry", {}).get("location", {}).get("lng")
        restaurants.append((name, address, rating, lat, lng))
    
    return restaurants

# Übersetzer Funktion
@st.cache_data
def translate(text):
    return GoogleTranslator(source="auto", target="de").translate(text)


# Streamlit UI
st.title("Sehen und Essen")

# Länderauswahl
country = st.session_state["land"]  
city = st.session_state["stadt"]

# Bedingung zum Abrufen der Daten
if st.session_state["land"] != "":
    location = city if city != "keine Stadt auswählen" else country
    
    # Sehenswürdigkeiten abrufen
    attractions = get_top_attractions(location)
    st.write("🏰 📸 🏯 📸 🕍 📸 🏟️ 📸 🕌 📸 ⛰️ 📸 ⛪️ 📸 🏰 📸 🏯 📸 🕍 📸 🏟️ 📸 🕌 📸 ⛰️ 📸 ⛪️ 📸 🏰 📸 🏯 📸 🕍 📸 🏟️ 📸 🕌 📸 ⛰️ 📸 ⛪️ 📸 🏰 📸 🏯 📸 🕍 📸 🏟️")
    st.write("")
    st.subheader(f"{location} hat viel zu bieten!")
    st.subheader(f"Hier sind die beliebtesten Sehenswürdigkeiten in {location}:")

        
    for i, (name, desc, image_url) in enumerate(attractions):
        
        col1, col2 = st.columns([2,2])

        with col1:
            st.write(f"### {name}")
            st.write(desc)
        
        with col2:
            if image_url:
                st.image(image_url, use_container_width=True)

    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    # Restaurants abrufen und Karte erstellen
    restaurants = get_best_restaurants(location)
    if restaurants:
        st.write("🍲 🥘 🥗 🌶️ 🫒 🥯 🥨 🥞 🥩 🍕 🥙 🌮 🫔 🫕 🥓 🍝 🍛 🍤 🥮 🥧 🍨 🍲 🥘 🥗 🌶️ 🫒 🥯 🥨 🥞 🥩 🍕 🥙 🌮 🫔 🫕 🥓 🍝 🍛 🍤 🥮 🥧 🍨 🍲 🥘 🥗 🌶️ 🫒 🥯 🥨")
        st.write("")
        st.subheader(f"Und wenn Du Hunger bekommst, empfehlen wir dir nur das Beste!")
        st.subheader(f"Hier findest Du die zehn bestbewerteten Restaurants in {location} :")

        st.markdown(
            """
            <style>
            .streamlit-container {
                width: 100% !important;
            }
            .folium-map {
                width: 100% !important;
                height: 500px !important;  /* Höhe anpassen, falls gewünscht */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        
        map_center = [restaurants[0][3], restaurants[0][4]] if restaurants else [0, 0]
        m = folium.Map(location=map_center, zoom_start=14)
        
        for name, address, rating, lat, lng in restaurants:
            folium.Marker([lat, lng], popup=f"{name}\n{address}").add_to(m)
        
        folium_static(m, width=800, height=500)
        
        col1, col2 = st.columns([2,2])
        
        with col1: 
            for name, address, rating, lat, lng in restaurants[:5]: 
                st.markdown(f"#### 👌 {name} ")
                st.markdown(f"📍{address}")
                st.markdown(f"⭐ Rating: {rating}")

        with col2: 
            for name, address, rating, lat, lng in restaurants[5:]: 
                st.markdown(f"#### 👌 {name} ")
                st.markdown(f"📍{address}")
                st.markdown(f"⭐ Rating: {rating}")


import streamlit as st
import wbgapi as wb
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import sys
import os


# Den übergeordneten Ordner zum sys.path hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from countries_and_cities import countries_and_cities


# session_state als Variablen initialisieren
code = st.session_state["alpha3"]
land = st.session_state["land"]

# Anzeige der aktuellen Auswahl in der Sidebar anzeigen
st.sidebar.write(f"**Aktuelle Auswahl:** {st.session_state['land']}" + (f" - {st.session_state['stadt']}" if st.session_state["stadt"] else ""))
st.sidebar.write("")
st.sidebar.markdown("Made with ❤️ by Carolin, Dina, Jonas, Laura")


# Weltbank Indikatoren definieren

# Firms with female top manager (% of firms)
fem_lead_perc = "IC.FRM.FEMM.ZS"

# Proportion of time spent on unpaid domestic and care work, female/male (% of 24 hour day)
unpaid_carework_f = "SG.TIM.UWRK.FE"
unpaid_carework_m = "SG.TIM.UWRK.MA"


# Diese Teile werden bisher nicht genutzt: 
# Part time employment, female (% of total female/male employment)
# parttime_f = "SL.TLF.PART.FE.ZS"
# parttime_m = "SL.TLF.PART.MA.ZS"

# Intentional homicides, female (per 100,000 female)
# int_homici_f = "VC.IHR.PSRC.FE.P5"
# int_homici_m = "VC.IHR.PSRC.MA.P5"

# Women participating in the three decisions 
# (own health care, major household purchases, and visiting family) (% of women age 15-49)
# decisions_f = "SG.DMK.ALLD.FN.ZS"

# Mortality caused by road traffic injury (per 100,000 population)
# traffic_mort = "SH.STA.TRAF.P5"



# Länder und IDs generieren
länder = list(countries_and_cities.keys())
ids = [data['iso_alpha_3'] for data in countries_and_cities.values()]

land_id = {k:v for k,v in zip(länder, ids)}

#################################################################

# Dataframe Firmen mit weibl ToP managern DataFrame erstellen
data_manager = wb.data.DataFrame(fem_lead_perc, economy=ids, mrv=1, skipBlanks=True)
# Index der Länder als Spalte hinzufügen
data_manager.reset_index(inplace=True)
# Spalten umbenennen
data_manager = data_manager.rename(columns={"economy": "country", "IC.FRM.FEMM.ZS": "Firms with Fem TopManager %"})
# ISO-Codes durch deutsche Ländernamen ersetzen (nur für vorhandene Länder)
mapping = {v: k for k, v in land_id.items() if v in data_manager['country'].values}
data_manager['country'] = data_manager['country'].map(mapping)
# data_manager["country"] = data_manager['country'].apply(lambda x: land for land in ids)
data_manager['highlight'] = data_manager['country'].apply(lambda x: 'markiert' if x == land else 'andere')

#################################################################

# Dataframe Care-Arbeit vorbereiten
care_work = wb.data.DataFrame([unpaid_carework_f, unpaid_carework_m], economy=ids, mrnev=1, skipBlanks=False)
care_work.reset_index(inplace=True)
# spalten umbenennen
care_work = care_work.rename(columns={"economy": "country", "SG.TIM.UWRK.FE": "women, % of 24h", "SG.TIM.UWRK.MA": "men, % of 24h" })
# ländernamen anstatt ländercode
mapping = {v: k for k, v in land_id.items() if v in care_work['country'].values}
care_work['country'] = care_work['country'].map(mapping)
# Berechnung der Differenz zwischen Frauen und Männern
care_work["diff"] = care_work["women, % of 24h"] - care_work["men, % of 24h"]
care_work['highlight'] = care_work['country'].apply(lambda x: 'markiert' if x == land else 'andere')

###################################################################

# UI in Streamlit

if st.session_state["land"] == "":
    st.title("Gleichstellung der Geschlechter")
    st.write("")
    st.write("")
    st.write(f"Gehe auf die Startseite und wähle ein Land aus!")

else: 
    st.title(f"Gleichstellung der Geschlechter in {land}")
    st.write("")
    st.header(f"⚥ Wie sieht es mit Gleichstellung zwischen Männern und Frauen in {land} aus? ")
    st.write("")
    st.write(f"📈 Nicht alle europäischen Länder stellen Daten zu diesem Thema zur Verfügung. Wenn {land} Daten zur Verfügung gestellt hat, wird es in dieser Grafik markiert")
    st.write("")
    st.write("")
    st.subheader(f"🤵 🤵‍♀️ Wie viele der Firmen in {land} werden von Frauen geführt? 🤵 🤵‍♀️")
    

    fig = px.bar(data_manager, x='country', y="Firms with Fem TopManager %", 
                 title="Firmen mit weiblicher Führungskraft (% der Firmen)",
                 labels={'country': 'Land', "Firms with Fem TopManager %": 'Prozent'}, 
                 color='highlight',  # Die Highlight-Spalte steuert die Farbe
                 color_discrete_map={"markiert": "red", "andere": "lightgrey"},  # Farben für Auswahl
                 text="Firms with Fem TopManager %")  # Textlabel für Prozentsatz anzeigen
    
    st.plotly_chart(fig)
    st.write("Quelle: Weltbank")

################################################################################################
    st.write("")
    st.write("")
    st.subheader(f"🪣 👶 🧼 🍼 🧹 🏠 🪣 👶 🧼 🍼 🧹 🏠 🪣 👶 🧼 🍼 🧹 🏠 🪣 👶 🧼 🍼 🧹 🏠 🪣 👶 🧼 ")
    st.subheader(f"Wie ist die unbezahlte Haus- und Sorgearbeit in {land} aufgeteilt? ")
    
    fig2 = px.scatter(care_work, 
                 x="diff", 
                 y="country", 
                 title="Differenz Frauen vs. Männer in Care-Arbeit",
                 labels={"diff": "Differenz (Frauen - Männer)", "country": "Land"},
                 size="diff",  # Punktgröße basierend auf der Differenz
                 size_max=30,  # Maximale Punktgröße anpassen
                 color="diff",  # Farbskala basierend auf der Differenz
                 color_discrete_map={'markiert': 'red'},
                 #color_continuous_scale='Viridis',
                opacity=0.7)  # Farbschema auswählen
    st.plotly_chart(fig2)
    st.write("Quelle: Weltbank")



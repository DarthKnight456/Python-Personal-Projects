import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut

st.title("Travel Budget Planner")

city_name = st.text_input(
    "Enter the city you want to visit:",
    placeholder="Space Needle, Seattle"
)

location = [48.8, 2.3]  # Default location
zoom = 4

if city_name:
    try:
        geolocator = Nominatim(
            user_agent="streamlit_map_app",
            timeout=10  # Increase timeout
        )

        location_data = geolocator.geocode(city_name)

        if location_data:
            location = [location_data.latitude, location_data.longitude]
            zoom = 10
        else:
            st.error("Location not found.")

    except (GeocoderTimedOut, GeocoderUnavailable):
        st.error("Unable to connect to the geocoding service. Please try again.")

m = folium.Map(location=location, zoom_start=zoom)
folium.Marker(location=location, popup=city_name).add_to(m)

st_folium(m, width=700, height=500)
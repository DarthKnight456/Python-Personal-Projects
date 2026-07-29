from dotenv import load_dotenv
import os

load_dotenv()

import json
import pandas as pd
import requests
import time

from openai import OpenAI


import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
from countryinfo import CountryInfo

st.title("Travel Budget Planner")

if "plan_result" not in st.session_state:
    st.session_state.plan_result = None

name = st.text_input(
    "Enter your name:",
    placeholder="John Doe"
)
roles = st.text_area(
    "Describe yourself (e.g., your interests, travel style):",
    placeholder="I enjoy cultural experiences and local cuisine."
)

length_of_trip = st.number_input(
    "Enter the length of your trip (in days):",
    placeholder="e.g., 5",
    min_value=1,
    step=1
)

destination_input = st.text_input(
    "Enter the city and country you wish to visit (format: city, country):",
    placeholder="Paris, France"
)

country_from = st.text_input(
    "Enter your current nation:",
    placeholder="United States"
)

budget = st.number_input(
    "Enter your total budget:",
    placeholder="e.g., 2000",
    min_value=0.0,
    step=1.0
)

submitted = st.button("Generate Summary and Budget Plan", type="primary", icon="💰")


def parse_destination(destination_input):
    if not destination_input:
        return None, None

    parts = [part.strip() for part in destination_input.split(",")]
    if len(parts) != 2 or not all(parts):
        return None, None

    return parts[0], parts[1]


def convert_currency(country_from, country_to, budget):
    try:
        budget_fixed = float(budget)
        country1 = CountryInfo(country_from)
        country2 = CountryInfo(country_to)

        currencies1 = country1.currencies()[0]
        currencies2 = country2.currencies()[0]
        url = f"https://v6.exchangerate-api.com/v6/{os.getenv('exchange_rate_key')}/pair/{currencies1}/{currencies2}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        conv_rate = float(data["conversion_rate"])
        conv_budget = budget_fixed * conv_rate
        return conv_budget, currencies2
    except (TypeError, ValueError, KeyError, requests.RequestException) as exc:
        st.warning(f"Could not convert the budget right now: {exc}")
        return None, None
    




def get_map(city_name):
    if city_name:
        try:
            geolocator = Nominatim(
                user_agent="streamlit_map_app",
                timeout=10  # Increase timeout
            )

            location_data = geolocator.geocode(city_name)

            if location_data:
                latitude = location_data.latitude
                longitude = location_data.longitude
                location = [latitude, longitude]
                map_data = pd.DataFrame(
                    [{"lat": latitude, "lon": longitude}]
                )
                zoom = 10
                return location, zoom, map_data
            else:
                st.error("Location not found.")

        except (GeocoderTimedOut, GeocoderUnavailable):
            st.error("Unable to connect to the geocoding service. Please try again.")







if submitted:
    with st.spinner("Wait for it...", show_time=True):
        time.sleep(5)
    
    if not name.strip() or not roles.strip() or not country_from.strip() or budget <= 0:
        st.warning("Please fill in all required fields before generating your plan.")
        st.stop()

    city_name, country_to = parse_destination(destination_input)
    if not city_name or not country_to:
        st.warning("Please enter the destination in the format 'city, country'.")
        st.stop()

    conv_budget, currencies2 = convert_currency(country_from, country_to, budget)
    if conv_budget is None:
        st.stop()
    location, zoom, map_data = get_map(city_name)
    if location is None:
        st.stop()

    

    st.write("Converted Budget from Currency Rates:", conv_budget, currencies2)
    
    with st.spinner("Wait for it...", show_time=True):
        time.sleep(5)
    try:
        client = OpenAI(api_key=os.getenv("openai_key"))

        response1 = client.responses.create(
            model="gpt-4o-mini",
            instructions=f"""You are an expert travel researcher. Your task is to provide a comprehensive, text-based overview of suggested accommodations and daily attractions for a specified destination, tailored to the user's personal description and trip duration. 

For the hotel:
- Recommend a highly rated, realistic accommodation type (e.g., hostel, boutique hotel, or luxury resort) matching their vibe.
- Provide the estimated average nightly cost in the destination's local currency.

For the itinerary attractions:
- Suggest 2 specific activities or sites to visit for each day of the trip.
- State the individual admission ticket price or entry fee for each attraction clearly in the local currency (specify if an attraction is free).

Keep your language descriptive, clear, and highly organized. Do not generate markdown tables, JSON objects, or spreadsheets. Present this strictly as a readable, text-based research summary.
However, if the budget is too low to cover any of the suggested accomodations or attractions, please provide alternative suggestions that fit within the budget constraints, and if no suitable options are available, please clearly state that the budget is insufficient for the trip and provide recommendations for adjusting the budget or travel plans accordingly.""",
            input=f"My name is {name} and I am a {roles} planning to visit {city_name} for {length_of_trip} days with a budget of {conv_budget:.2f}{currencies2}. Here is some additional information that needs to be considered as well:"
        )
        with st.spinner("Wait for it...", show_time=True):
            time.sleep(5)
        st.write(response1.output_text)

        response2 = client.responses.create(
            model="gpt-4o-mini",
            instructions="""You are a travel advisor financialist who creates budget plans for users who want to travel to a specific city or place.
            Organize the budget according to categories of the Day, Food, Transporation, Tickets, and Misc, and allocate higher or lower percentages of the budget on the categories based on the previous travel information, """ + response1.output_text + """. Give the answer in just JSON format for the table only like this, and don't give any other text or markdown ticks or text besides what is shown on the JSON template. However, don't generate anything including the day #, even the first one, and leave it blank if the budget is found to be insufficient for the trip based on the previous travel information and recommendations. Here is the JSON template, but don't generate the template if the budget is insufficient for the trip based on the previous travel information and recommendations:
            [
            {
                "Day #": 1,
                "Food": budget,
                "Transportation": budget,
                "Hotel Stay": budget,
                "Attractions/Tickets": budget,
                "Misc": budget
            }
        ]

            """,
            input=f"My name is {name}, and I am going to visit {city_name} for {length_of_trip} days. My budget is {conv_budget:.2f} {currencies2}. Here is some additional information that needs to be considered as well:"
        )
        st.text("Here is an interactive map of your destination:")
     
        st.map(map_data, zoom=zoom)
        
      
        
        data = json.loads(response2.output_text)
        if not data:
            st.warning("The budget is insufficient for the trip based on the previous travel information and recommendations. Please consider adjusting your budget or travel plans.")
        else:
            df = pd.DataFrame(data)
            st.write("Here is your budget plan:")
            st.dataframe(df)
            st.success("Your travel summary and budget plan have been generated successfully!")
        with st.spinner("Almost done...", show_time=True):
            time.sleep(5)
        
     
    except requests.RequestException as req_exc:
        st.warning(f"There was a network error while generating the budget plan: {req_exc}")
    except Exception as exc:
        st.warning(f"The budget plan could not be generated right now: {exc}")
    

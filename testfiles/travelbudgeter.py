from dotenv import load_dotenv
import os

load_dotenv()
import os
from urllib import response

from openai import OpenAI
import json
import pandas as pd
import sys
import time
import requests
from countryinfo import CountryInfo
name, roles, length = input("Hello, this is your AI Budgeter Agent! Please give me your name, a description about yourself, and length of your trip to get started(# days): ").split(",")
city, country_to = input("Please enter the city and country you wish to visit(city, country): ").split(",")
advanced_pref = []
while True:
    extra = input("Would you like to give any other additional preferences to specialize or enhance the budget information?")
    if extra in ("yes", "y", "Yes", "YES"):
        add_inf = input("Describe additional preferences and information(be as specific as possible): ")
        advanced_pref.append(add_inf)
    elif extra in ("no", "n", "No", "NO"):
        break
    else:
        ("Your input is not valid, please type 'yes' or 'no'")
country_from, budget = input("Finally, give your current nation, and the total budget: ").split(",")


def convert_currency(country_from, country_to, budget):
    budget_fixed = float(budget)
    country1 = CountryInfo(country_from)
    country2 = CountryInfo(country_to)

    currencies1 = country1.currencies()[0]
    currencies2 = country2.currencies()[0]
    url = f"https://v6.exchangerate-api.com/v6/{os.getenv('exchange_rate_key')}/pair/{currencies1}/{currencies2}"
    response = requests.get(url)
    data = response.json()
    conv_rate = float(data["conversion_rate"])
    try:
        conv_budget = budget_fixed * conv_rate
        return conv_budget, currencies2
    except TypeError:
        print("You have entered a invalid value, please go back and fix it")

conv_budget, currencies2 = convert_currency(country_from, country_to, budget)










client = OpenAI(api_key = os.getenv("openai_key"))


response1 = client.responses.create(
    model="gpt-4o-mini",
    instructions = f"""You are an expert travel researcher. Your task is to provide a comprehensive, text-based overview of suggested accommodations and daily attractions for a specified destination, tailored to the user's personal description and trip duration. 

For the hotel:
- Recommend a highly rated, realistic accommodation type (e.g., hostel, boutique hotel, or luxury resort) matching their vibe.
- Provide the estimated average nightly cost in the destination's local currency.

For the itinerary attractions:
- Suggest 2 specific activities or sites to visit for each day of the trip.
- State the individual admission ticket price or entry fee for each attraction clearly in the local currency (specify if an attraction is free).

Keep your language descriptive, clear, and highly organized. Do not generate markdown tables, JSON objects, or spreadsheets. Present this strictly as a readable, text-based research summary.""",
    input = f"My name is {name} and I am a {roles} planning to visit {city} for {length} days. Here is some additional information that needs to be considered as well: {advanced_pref}"

)
print(response1.output_text) 



print("Converted Budget from Currency Rates: ", conv_budget, currencies2)


response2 = client.responses.create(
    model="gpt-4o-mini",
    instructions = """You are a travel advisor financialist who creates budget plans for users who want to travel to a specific city or place.
    Organize the budget according to categories of the Day, Food, Transporation, Tickets, and Misc, and allocate higher or lower percentages of the budget on the categories based on the previous travel information, """ + response1.output_text + """. Give the answer in just JSON format for the table only like this, and don't give any other text or markdown ticks or text besides what is shown on the JSON template:
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
    input= f"My name is {name}, and I am going to visit{city} for {length} days. My budget is {conv_budget} {currencies2}. Here is some additional information that needs to be considered as well: {advanced_pref}"
)

data = json.loads(response2.output_text)
df = pd.DataFrame(data)

print(df)


    
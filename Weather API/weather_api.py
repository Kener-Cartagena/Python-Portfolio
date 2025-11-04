import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_weather_data(city):
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    response = requests.get(api)
    data = response.json()

    if data.get("cod") != 200:
        raise ValueError(data.get("message", "City not found"))

    weather = {
        "condition": data['weather'][0]['main'],
        "description": data['weather'][0]['description'],
        "temp": int(data['main']['temp'] - 273.15),
        "pressure": data['main']['pressure'],
        "humidity": data['main']['humidity'],
        "wind": data['wind']['speed'],
    }

    return weather

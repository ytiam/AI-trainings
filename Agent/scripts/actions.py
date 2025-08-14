import requests
from textblob import TextBlob
from dotenv import load_dotenv
load_dotenv()
import os

def generate_character_name(character_type):
    names = {
        "wizard": "Gandalf the Grey",
        "knight": "Sir Lancelot",
        "villain": "Lord Voldemort",
        "scientist": "Dr. Emmett Brown",
        "detective": "Sherlock Holmes",
    }
    return names.get(character_type, "Unknown Character")

def determine_character_trait(character_name):
    traits = {
        "Gandalf the Grey": "wise and powerful",
        "Sir Lancelot": "brave and chivalrous",
        "Lord Voldemort": "cunning and ruthless",
        "Dr. Emmett Brown": "eccentric and genius",
        "Sherlock Holmes": "observant and logical",
    }
    return traits.get(character_name, "trait unknown")

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity  # Returns a value between -1 (negative) and 1 (positive)

def fetch_current_weather(location):
    api_key = os.getenv("weather_api_key")  # Replace with your weather API key
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}"
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        return f"The current temperature in {location} is {weather_data['current']['temp_c']}°C"
    else:
        return "Unable to fetch weather data at the moment."
import requests
from textblob import TextBlob
from sympy import symbols, Eq, solve, sympify
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
    
def solve_equation(equation):
    """
    Solves a given algebraic equation and returns the solution(s).

    Args:
        equation (str): An equation as a string, e.g., "2*x + 5 = 15"

    Returns:
        dict: {
            "equation": "<original equation>",
            "solutions": [list of solutions as strings]
        }
    """
    try:
        # Split equation into LHS and RHS
        if "=" not in equation:
            return {
                "equation": equation,
                "error": "Equation must contain '=' sign"
            }
        
        lhs, rhs = equation.split("=")
        lhs = sympify(lhs.strip())
        rhs = sympify(rhs.strip())
        
        # Detect variables
        vars_in_eq = list(lhs.free_symbols.union(rhs.free_symbols))
        if not vars_in_eq:
            return {
                "equation": equation,
                "error": "No variable found in equation"
            }
        
        # Assume solving for the first variable
        var = vars_in_eq[0]
        solutions = solve(Eq(lhs, rhs), var)
        
        return {
            "equation": equation,
            "solutions": [str(s) for s in solutions]
        }
    
    except Exception as e:
        return {
            "equation": equation,
            "error": str(e)
        }

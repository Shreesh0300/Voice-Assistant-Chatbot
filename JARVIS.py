import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import requests

# --- SETUP ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")
if not WEATHER_API_KEY:
    print("WARNING: WEATHER_API_KEY not found. The weather function will not work.")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-pro-latest")
app = Flask(__name__)
CORS(app)

# --- HELPER FUNCTIONS ---
def generate_response(user_input):
    try:
        response = model.generate_content(user_input)
        return response.text.strip()
    except Exception as e:
        print(f"--- GEMINI ERROR ---: {e}")
        return "Sorry, I had an issue connecting to my AI brain."

def get_weather(city_name):
    if not WEATHER_API_KEY:
        return "Sorry, my weather API key is not configured."
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": WEATHER_API_KEY, "units": "metric"}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        return f"The weather in {city_name} is {weather} with a temperature of {temperature}°C."
    else:
        return f"Sorry, I failed to retrieve weather data for {city_name}."

def handle_message(message):
    msg_lower = message.lower()

    # --- NEW: Handle "open" commands ---
    if msg_lower.startswith("open "):
        # Basic parsing to get the site name (e.g., "youtube", "google")
        site_name = msg_lower.replace("open ", "").strip().lower()
        # You can create a dictionary for specific URLs
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "wikipedia": "https://www.wikipedia.org"
        }
        url_to_open = sites.get(site_name, f"https://www.{site_name}.com")
        
        return {
            "text": f"Opening {site_name}...",
            "action": "open_url",
            "url": url_to_open
        }

    elif "weather in" in msg_lower:
        city = msg_lower.split("weather in")[-1].strip()
        return get_weather(city) if city else "Which city's weather?"
    elif "weather" in msg_lower:
        return "Of course. Please ask again using the format: 'weather in {city name}'."
    else:
        return generate_response(message)

# --- UPDATED API ENDPOINT ---
@app.route("/ask", methods=['POST'])
def ask_assistant():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    assistant_response = handle_message(user_message)
    
    # Check if the response is a special command object or just text
    if isinstance(assistant_response, dict):
        return jsonify(assistant_response)
    else:
        return jsonify({"text": assistant_response})

# --- FRONTEND ROUTE ---
@app.route("/")
def home():
    return render_template("index.html")

# --- RUN SERVER ---
if __name__ == "__main__":
    app.run(debug=True, port=5000)
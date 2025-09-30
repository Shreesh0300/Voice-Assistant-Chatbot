import os
import sys
import google.generativeai as genai
import webbrowser
import sys
import requests
from dotenv import load_dotenv
from voice_assistant import speak, listen  # Your own voice functions
from datetime_utils import handle_datetime_message  # Import datetime handler

# --- 1. Load API Keys Securely ---
load_dotenv() # This loads the variables from the .env file

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Check if keys were loaded and exit if they are missing
if not GEMINI_API_KEY or not WEATHER_API_KEY:
    print("Error: API keys not found. Make sure you have a .env file with GEMINI_API_KEY and WEATHER_API_KEY.")
    sys.exit(1)

# --- 2. Configure Gemini API (Only Once) ---
genai.configure(api_key=GEMINI_API_KEY)

# --- 3. Initialize Models ---
multilingual_model = genai.GenerativeModel("gemini-1.5-flash")
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat()

# --- Your Existing Code (Unchanged) ---

def generate_response(user_input):
    prompt = (
        f"Detect the language of this message and respond in the same language:\n"
        f"{user_input}\n"
        "Reply naturally in that language only."
    )
    try:
        response = multilingual_model.generate_content(prompt)
        reply = response.text.strip() if response and hasattr(response, "text") else "Sorry, I could not generate a response."
    except Exception as e:
        print(f"Gemini error: {e}")
        reply = "Sorry, I couldn't process your request."
    return reply

notes = []  # Store notes here

# --- User profile with favorite websites ---
user_profile = {
    "name": "Shreesh",
    "preferred_language": "English",
    "voice_speed": 150,
    "favorite_websites": [
        "https://www.google.com",
        "https://www.youtube.com",
        "https://netmirror.app"
    ]
}

# === Fun Request Handler ===
def handle_fun_requests(message, model, speak):
    lower_message = message.lower()
    if "tell me a joke" in lower_message:
        response = model.generate_content("Tell me a joke.")
        speak(response.text)
        return True
    elif "fun fact" in lower_message:
        response = model.generate_content("Tell me a fun fact.")
        speak(response.text)
        return True
    return False

def open_website(url):
    print(f"Opening: {url}")
    webbrowser.open(url)
    speak(f"Opening {url}")

def open_favorite_website(user_profile, speak, index=0):
    favorites = user_profile.get("favorite_websites", [])
    if 0 <= index < len(favorites):
        url = favorites[index]
        print(f"Assistant: Opening your favorite website: {url}")
        webbrowser.open(url)
        speak(f"Opening your favorite website: {url}")
    else:
        speak("You don't have a favorite website set or the index is out of range.")
        print("Assistant: You don't have a favorite website set or the index is out of range.")

def get_weather(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        result = f"Weather in {city_name}: {weather}. Temperature: {temperature}°C"
        print(result)
        speak(result)
    else:
        error_msg = f"Failed to retrieve weather data for {city_name}. Error code: {response.status_code}"
        print(error_msg)
        speak(error_msg)

def handle_message(message):
    msg_lower = message.lower()

    if handle_fun_requests(message, model, speak):
        return True
    if handle_datetime_message(message, speak):
        return True

    if "take a note" in msg_lower:
        speak("What would you like me to note?")
        note = listen()
        if note:
            notes.append(note)
            speak("Note saved.")
        else:
            speak("I didn't catch your note.")
        return True
    elif "read my notes" in msg_lower:
        if notes:
            speak("Here are your notes:")
            for i, note in enumerate(notes, 1):
                speak(f"Note {i}: {note}")
        else:
            speak("You don't have any notes.")
        return True
    elif "summarize" in msg_lower:
        speak("Please say the content you want me to summarize.")
        content = listen()
        if content:
            response = model.generate_content("Summarize this: " + content)
            speak(response.text)
        else:
            speak("I didn't catch any content to summarize.")
        return True
    elif "open favourite website" in msg_lower:
        import re
        match = re.search(r'open favorite website\s*(\d+)?', msg_lower)
        if match and match.group(1):
            index = int(match.group(1)) - 1
        else:
            index = 0
        open_favorite_website(user_profile, speak, index)
        return True

    if "search google for" in msg_lower:
        query = msg_lower.replace("search google for", "").strip()
        url = f"https://www.google.com/search?q={query}"
        open_website(url)
        return True
    elif "search youtube for" in msg_lower:
        query = msg_lower.replace("search youtube for", "").strip()
        url = f"https://www.youtube.com/results?search_query={query}"
        open_website(url)
        return True
    elif msg_lower in ['bye', 'goodbye']:
        print("Chatbot: Goodbye!")
        speak("Goodbye!")
        sys.exit()
    elif "weather" in msg_lower:
        speak("For which city would you like the weather?")
        city = listen()
        if city:
            # Pass the WEATHER_API_KEY variable to the function
            get_weather(city, WEATHER_API_KEY)
    elif "open website" in msg_lower:
        speak("Which website would you like to open?")
        website = listen()
        if website:
            if not website.startswith("http"):
                website = "https://" + website + ".com/"
            open_website(website)
    elif "open youtube" in msg_lower:
        open_website("https://www.youtube.com/")
    elif "open google" in msg_lower:
        open_website("https://www.google.com/")
    elif "open netmirror" in msg_lower:
        open_website("https://netmirror.app/")
    elif "open facebook" in msg_lower:
        open_website("https://www.facebook.com/")
    elif ("open watsap" in msg_lower or "open whatsapp" in msg_lower or "open x" in msg_lower):
        open_website("https://web.whatsapp.com/")
    else:
        response = generate_response(message) # Using the multilingual function
        print(f"Chatbot: {response}")
        speak(response)
    return True

def main():
    speak("Hello Shreesh How are you doing?")
    while True:
        message = listen()
        if not message:
            continue
        handle_message(message)

if __name__ == "__main__":
    main()
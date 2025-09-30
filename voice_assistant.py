import pyttsx3
import speech_recognition as sr

# Initialize the text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    """
    Converts text to speech.
    """
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """
    Listens for a voice command and converts it to text.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User: {query}")
        return query.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Please try again.")
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""
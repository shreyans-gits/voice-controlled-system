from core.brain import Brain
from core.voice import Voice
import config
from modules.weather import WeatherModule

import datetime
import time


def greet():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return f"Good morning {config.USER_NAME}. NOVA online."
    elif hour < 18:
        return f"Good afternoon {config.USER_NAME}. NOVA online."
    else:
        return f"Good evening {config.USER_NAME}. NOVA online."

def main():
    brain = Brain()
    voice = Voice()
    weather = WeatherModule()

    voice.speak(greet())

    while True:
        query = voice.listen()

        if not query:
            continue

        if "quit" in query or "exit" in query or "goodbye" in query:
            voice.speak("Shutting down. Goodbye.")
            break

        elif "weather" in query:
            voice.speak(weather.getWeather())

        else:
            response = brain.ask(query)
            voice.speak(response)

if __name__ == "__main__":
    main()
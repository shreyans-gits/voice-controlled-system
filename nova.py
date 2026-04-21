from core.brain import Brain
from core.voice import Voice
import config
from modules.weather import WeatherModule
from modules.system import SystemModule
from modules.search import SearchModule
from modules.news import NewsModule
from modules.reminder import ReminderModule
from modules.whatsapp import WhatsappModule
from modules.spotify import SpotifyModule
from modules.study import StudyModule

import datetime
import time
import threading
from plyer import notification

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
    system = SystemModule()
    search = SearchModule()
    news = NewsModule()
    reminder = ReminderModule()
    wp = WhatsappModule()
    spotify = SpotifyModule()
    study = StudyModule()

    def reminder_checker():
        while True:
            alert = reminder.check_reminders()
            if alert:
                voice.speak(f"Reminder: {alert}")
                notification.notify(
                    title = "REMINDER!",
                    message = alert,
                    timeout = 5
                )

            time.sleep(30)

    threading.Thread(target=reminder_checker, daemon=True).start()


    voice.speak(greet())

    while True:
        query = voice.listen()

        if not query:
            continue

        if "quit" in query or "exit" in query or "goodbye" in query:
            voice.speak("Shutting down. Goodbye.")
            break
        else:
            intent = brain.get_intent(query)

            if intent == "WEATHER":
                voice.speak(weather.getWeather())

            elif intent == "BATTERY":
                voice.speak(system.get_battery())
            elif intent == "CPU":
                voice.speak(system.get_cpu())
            elif intent == "RAM":
                voice.speak(system.get_ram())

            elif intent == "SEARCH":
                subject = brain.extract_subject(query, intent)
                voice.speak(f"Searching {subject}")
                search.search(subject)
            elif intent == "WATCH":
                subject = brain.extract_subject(query, intent)
                voice.speak(f"Searching {subject} on YouTube")
                search.watch(subject)
            elif intent == "WIKIPEDIA":
                subject = brain.extract_subject(query, intent)
                voice.speak("Searching Wikipedia...")
                voice.speak(search.getWiki(subject))

            elif intent == "NEWS":
                titles = news.get_news()
                for i in titles:
                    voice.speak(i)

            elif intent == "REMINDER":
                voice.speak("What should I remind you about?")
                message = voice.listen()
                voice.speak("In how many minutes?")
                time_str = voice.listen()
                voice.speak(reminder.set_reminder(time_str, message))

            elif intent == "WHATSAPP":
                voice.speak("What is your message?")
                message = voice.listen()
                message = message + "\n\n_- This message was sent to you by NOVA_"
                voice.speak("To whom do you want to send the message?")
                name = voice.listen().lower()
                number = config.CONTACTS.get(name, "+916363466319")
                if name not in config.CONTACTS:
                    voice.speak(f"I couldn't find {name} in your contacts, so I'll send it to your default number.")
                voice.speak(wp.send_message(number,message))

            elif intent == "SPOTIFY_PLAY":
                subject = brain.extract_subject(query, intent)
                voice.speak(f"Searching for {subject} on Spotify")
                result = spotify.play(subject)
                voice.speak(result)
            elif intent == "SPOTIFY_PAUSE":
                voice.speak(spotify.pause())
            elif intent == "SPOTIFY_SKIP":
                voice.speak(spotify.next_track())

            elif intent == "POMODORO":
                try:
                    mins = int(query.split("for")[1].split()[0])
                    voice.speak(study.pomodoro(mins))
                except:
                    voice.speak(study.pomodoro(25))
            elif intent == "SUMMARIZE":
                summary_result = study.summarize_pdf() 
                voice.speak(summary_result)
            elif intent == "FLASHCARD":
                voice.speak("Give name of the topic")
                topic = voice.listen().lower()
                if topic:
                    voice.speak(f"Generating flashcards for {topic}. Just a moment.")
                    voice.speak(study.flashcard(topic))
                else:
                    voice.speak("I didn't catch the topic. Please try again.")

            else:
                response = brain.ask(query)
                voice.speak(response)

if __name__ == "__main__":
    main()
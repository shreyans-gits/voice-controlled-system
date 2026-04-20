from core.brain import Brain
from core.voice import Voice
import config
from modules.weather import WeatherModule
from modules.system import SystemModule
from modules.search import SearchModule
from modules.news import NewsModule
from modules.reminder import ReminderModule
from modules.whatsapp import WhatsappModule

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

        elif "weather" in query:
            voice.speak(weather.getWeather())

        elif "battery" in query:
            voice.speak(system.get_battery())
        elif "cpu" in query:
            voice.speak(system.get_cpu())
        elif "ram usage" in query or "memory" in query:
            voice.speak(system.get_ram())

        elif "search" in query or "find" in query:
            query = query.replace("search", ' ')
            query = query.replace("find", ' ')
            voice.speak(f"Searching {query}")
            search.search(query)
        elif "watch" in query:
            query = query.replace("watch", ' ')
            voice.speak(f"Searching {query}")
            search.watch(query)
        elif "wiki" in query or "wikipedia" in query:
            voice.speak("Searching Wikipedia...")
            query = query.replace("wikipedia", "")
            query = query.replace("wiki", "")
            voice.speak(search.getWiki(query))

        elif "news" in query:
            titles = news.get_news()
            for i in titles:
                voice.speak(i)

        elif "reminder" in query:
            voice.speak("What should I remind you about?")
            message = voice.listen()
            voice.speak("In how many minutes?")
            time_str = voice.listen()
            voice.speak(reminder.set_reminder(time_str, message))

        elif "message" in query:
            voice.speak("What is your message?")
            message = voice.listen()
            message = message + "\n\n_- This message was sent to you by NOVA_"
            voice.speak("To whom do you want to send the message?")
            name = voice.listen().lower()
            number = config.CONTACTS.get(name, "+916363466319")
            if name not in config.CONTACTS:
                voice.speak(f"I couldn't find {name} in your contacts, so I'll send it to your default number.")
            voice.speak(wp.send_message(number,message))

        else:
            response = brain.ask(query)
            voice.speak(response)

if __name__ == "__main__":
    main()
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

from gui.dashboard import Dashboard

import datetime
import time
import threading
from plyer import notification
import queue

def greet():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return f"Good morning {config.USER_NAME}. NOVA online."
    elif hour < 18:
        return f"Good afternoon {config.USER_NAME}. NOVA online."
    else:
        return f"Good evening {config.USER_NAME}. NOVA online."

def main(dashboard,message_queue):
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
                message_queue.put({"type": "message", "sender": "NOVA", "text": alert})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(f"Reminder: {alert}")
                message_queue.put({"type": "status", "value": "LISTENING"})
                notification.notify(
                    title = "REMINDER!",
                    message = alert,
                    timeout = 5
                )

            time.sleep(30)

    threading.Thread(target=reminder_checker, daemon=True).start()

    message_queue.put({"type": "message", "sender": "NOVA", "text": greet()})
    message_queue.put({"type": "status", "value": "SPEAKING"})
    voice.speak(greet())
    message_queue.put({"type": "status", "value": "LISTENING"})

    while True:
        query = ""
        try:
            msg = message_queue.get_nowait()
            if msg["type"] == "text_input":
                query = msg["text"]
        except:
            pass

        if not query:
            message_queue.put({"type": "status", "value": "LISTENING"})
            query = voice.listen()

        if not query:
            continue
        message_queue.put({"type": "message", "sender": "You", "text": query})
        message_queue.put({"type": "status", "value": "THINKING"})

        if "quit" in query or "exit" in query or "goodbye" in query:
            message_queue.put({"type": "message", "sender": "NOVA", "text": "Shutting down. Goodbye."})
            message_queue.put({"type": "status", "value": "SPEAKING"})
            voice.speak("Shutting down. Goodbye.")
            message_queue.put({"type": "status", "value": "LISTENING"})
            dashboard.after(0, dashboard.destroy)
            break
        else:
            intent = brain.get_intent(query)

            if intent == "WEATHER":
                message_queue.put({"type": "message", "sender": "NOVA", "text": weather.getWeather()})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(weather.getWeather())
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "BATTERY":
                message_queue.put({"type": "message", "sender": "NOVA", "text": system.get_battery()})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(system.get_battery())
                message_queue.put({"type": "status", "value": "LISTENING"})
            elif intent == "CPU":
                message_queue.put({"type": "message", "sender": "NOVA", "text": system.get_cpu()})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(system.get_cpu())
                message_queue.put({"type": "status", "value": "LISTENING"})
            elif intent == "RAM":
                message_queue.put({"type": "message", "sender": "NOVA", "text": system.get_ram()})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(system.get_ram())
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "SEARCH":
                subject = brain.extract_subject(query, intent)
                message_queue.put({"type": "message", "sender": "NOVA", "text": f"Searching {subject}"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(f"Searching {subject}")
                message_queue.put({"type": "status", "value": "LISTENING"})
                search.search(subject)
            elif intent == "WATCH":
                subject = brain.extract_subject(query, intent)
                message_queue.put({"type": "message", "sender": "NOVA", "text": f"Searching {subject} on YouTube"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(f"Searching {subject} on YouTube")
                message_queue.put({"type": "status", "value": "LISTENING"})
                search.watch(subject)
            elif intent == "WIKIPEDIA":
                subject = brain.extract_subject(query, intent)
                message_queue.put({"type": "message", "sender": "NOVA", "text": "Searching Wikipedia..."})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak("Searching Wikipedia...")
                message_queue.put({"type": "status", "value": "LISTENING"})
                message_queue.put({"type": "message", "sender": "NOVA", "text": search.getWiki(subject)})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(search.getWiki(subject))
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "NEWS":
                titles = news.get_news()
                for i in titles:
                    message_queue.put({"type": "message", "sender": "NOVA", "text": i})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(i)
                    message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "REMINDER":
                message_queue.put({"type": "message", "sender": "NOVA", "text": "What should I remind you about?"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak("What should I remind you about?")
                message_queue.put({"type": "status", "value": "LISTENING"})
                message = voice.listen()
                message_queue.put({"type": "message", "sender": "You", "text": query})
                message_queue.put({"type": "message", "sender": "NOVA", "text": "In how many minutes?"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak("In how many minutes?")
                message_queue.put({"type": "status", "value": "LISTENING"})
                time_str = voice.listen()
                message_queue.put({"type": "message", "sender": "You", "text": query})
                message_queue.put({"type": "message", "sender": "NOVA", "text": reminder.set_reminder(time_str, message)})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(reminder.set_reminder(time_str, message))
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "WHATSAPP":
                message_queue.put({"type": "message", "sender": "NOVA", "text": "What is your message?"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak("What is your message?")
                message_queue.put({"type": "status", "value": "LISTENING"})
                message = voice.listen()
                message_queue.put({"type": "message", "sender": "You", "text": query})
                message = message + "\n\n_- This message was sent to you by NOVA_"
                message_queue.put({"type": "message", "sender": "NOVA", "text": "To whom do you want to send the message?"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak("To whom do you want to send the message?")
                message_queue.put({"type": "status", "value": "LISTENING"})
                name = voice.listen().lower()
                message_queue.put({"type": "message", "sender": "You", "text": query})
                number = config.CONTACTS.get(name, "+916363466319")
                if name not in config.CONTACTS:
                    message_queue.put({"type": "message", "sender": "NOVA", "text": f"I couldn't find {name} in your contacts, so I'll send it to your default number."})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(f"I couldn't find {name} in your contacts, so I'll send it to your default number.")
                    message_queue.put({"type": "status", "value": "LISTENING"})
                message_queue.put({"type": "message", "sender": "NOVA", "text": wp.send_message(number,message)})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(wp.send_message(number,message))
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "SPOTIFY_PLAY":
                subject = brain.extract_subject(query, intent)
                message_queue.put({"type": "message", "sender": "NOVA", "text": f"Searching for {subject} on Spotify"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(f"Searching for {subject} on Spotify")
                message_queue.put({"type": "status", "value": "LISTENING"})
                result = spotify.play(subject)
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})
            elif intent == "SPOTIFY_PAUSE":
                message_queue.put({"type": "message", "sender": "NOVA", "text": spotify.pause()})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(spotify.pause())
                message_queue.put({"type": "status", "value": "LISTENING"})
            elif intent == "SPOTIFY_SKIP":
                message_queue.put({"type": "message", "sender": "NOVA", "text": spotify.next_track()})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(spotify.next_track())
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "POMODORO":
                try:
                    mins = int(query.split("for")[1].split()[0])
                    message_queue.put({"type": "message", "sender": "NOVA", "text": study.pomodoro(mins)})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(study.pomodoro(mins))
                    message_queue.put({"type": "status", "value": "LISTENING"})
                except:
                    message_queue.put({"type": "message", "sender": "NOVA", "text": study.pomodoro(25)})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(study.pomodoro(25))
                    message_queue.put({"type": "status", "value": "LISTENING"})
            elif intent == "SUMMARIZE":
                summary_result = study.summarize_pdf() 
                message_queue.put({"type": "message", "sender": "NOVA", "text": summary_result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(summary_result)
                message_queue.put({"type": "status", "value": "LISTENING"})
            elif intent == "FLASHCARD":
                message_queue.put({"type": "message", "sender": "NOVA", "text": "Give name of the topic"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak("Give name of the topic")
                message_queue.put({"type": "status", "value": "LISTENING"})
                topic = voice.listen().lower()
                message_queue.put({"type": "message", "sender": "You", "text": query})
                if topic:
                    message_queue.put({"type": "message", "sender": "NOVA", "text": f"Generating flashcards for {topic}. Just a moment."})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(f"Generating flashcards for {topic}. Just a moment.")
                    message_queue.put({"type": "status", "value": "LISTENING"})
                    message_queue.put({"type": "message", "sender": "NOVA", "text": study.flashcard(topic)})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(study.flashcard(topic))
                    message_queue.put({"type": "status", "value": "LISTENING"})
                else:
                    message_queue.put({"type": "message", "sender": "NOVA", "text": "I didn't catch the topic. Please try again."})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak("I didn't catch the topic. Please try again.")
                    message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "CONVERSATION":
                response = brain.ask(query)
                message_queue.put({"type": "message", "sender": "NOVA", "text": response})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(response)
                message_queue.put({"type": "status", "value": "LISTENING"})

            else:
                response = brain.ask(query)
                message_queue.put({"type": "message", "sender": "NOVA", "text": response})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(response)
                message_queue.put({"type": "status", "value": "LISTENING"})

if __name__ == "__main__":
    message_queue = queue.Queue()
    app = Dashboard(message_queue)
    
    nova_thread = threading.Thread(
        target=main, 
        args=(app, message_queue),
        daemon=True
    )
    nova_thread.start()

    app.check_queue(message_queue)
    app.mainloop()
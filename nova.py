import datetime
import time
import threading
from plyer import notification
import queue
import os

import sys
import types

venv_site = r"e:\ek-gits\NOVA\venv\Lib\site-packages"
m_dir = os.path.join(venv_site, "face_recognition_models", "models")
m = types.ModuleType("face_recognition_models")
m.pose_predictor_model_location = lambda: os.path.join(m_dir, "shape_predictor_68_face_landmarks.dat")
m.pose_predictor_five_point_model_location = lambda: os.path.join(m_dir, "shape_predictor_5_face_landmarks.dat")
m.face_recognition_model_location = lambda: os.path.join(m_dir, "dlib_face_recognition_resnet_model_v1.dat")
m.cnn_face_detector_model_location = lambda: os.path.join(m_dir, "mmod_human_face_detector.dat")
sys.modules["face_recognition_models"] = m

print("Successfully spoofed face_recognition_models.")

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
from modules.screen_reader import ScreenReaderModule
from modules.app_launcher import AppLauncherModule
from modules.clipboard import Clipboard
from modules.system_control import SystemControlModule
from modules.voice_note import VoiceNoteModule

from skills.gesture.gesture import GestureModule
from skills.facelink.facelink import FaceLink
from skills.model_gen.model_gen import ModelGenModule

from core.memory import Memory

from gui.dashboard import Dashboard
from gui.settings import SettingsWindow


def greet():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return f"Good morning {config.USER_NAME}. NOVA online."
    elif hour < 18:
        return f"Good afternoon {config.USER_NAME}. NOVA online."
    else:
        return f"Good evening {config.USER_NAME}. NOVA online."

def main(dashboard,message_queue,input_queue):
    memory = Memory()
    brain = Brain(system_prompt_addition=memory.summary)
    voice = Voice()
    weather = WeatherModule()
    system = SystemModule()
    search = SearchModule()
    news = NewsModule()
    reminder = ReminderModule()
    wp = WhatsappModule()
    spotify = SpotifyModule()
    study = StudyModule()
    screen = ScreenReaderModule()
    launcher = AppLauncherModule()
    clipboard = Clipboard()
    systemControl = SystemControlModule()
    voice_note = VoiceNoteModule()

    gesture = GestureModule()
    facelink = FaceLink()
    model_gen = ModelGenModule()

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
        message_queue.put({"type": "status", "value": "LISTENING"})
        
        voice_result = [None]
        def do_listen():
            voice_result[0] = voice.listen()
        
        listen_thread = threading.Thread(target=do_listen, daemon=True)
        listen_thread.start()
        
        while listen_thread.is_alive():
            try:
                msg = input_queue.get_nowait()
                query = msg["text"]
                break
            except:
                time.sleep(0.1)
        
        if not query:
            listen_thread.join()
            query = voice_result[0]

        message_queue.put({"type": "message", "sender": "You", "text": query})
        message_queue.put({"type": "status", "value": "THINKING"})

        if "quit" in query or "exit" in query or "goodbye" in query:
            message_queue.put({"type": "message", "sender": "NOVA", "text": "Shutting down. Goodbye."})
            message_queue.put({"type": "status", "value": "SPEAKING"})
            voice.speak("Summarizing session memory...")
            memory.summarize_and_save(brain)
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
                message_queue.put({"type": "message", "sender": "You", "text": message})
                message = message + "\n\n_- This message was sent to you by NOVA_"
                message_queue.put({"type": "message", "sender": "NOVA", "text": "To whom do you want to send the message?"})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak("To whom do you want to send the message?")
                message_queue.put({"type": "status", "value": "LISTENING"})
                name = voice.listen().lower()
                message_queue.put({"type": "message", "sender": "You", "text": name})
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

            elif intent == "SCREEN_READ":
                message_queue.put({"type": "status", "value": "THINKING"})
                result = screen.read("Describe everything on this screen")
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "SCREEN_EXPLAIN":
                message_queue.put({"type": "status", "value": "THINKING"})
                result = screen.read("Explain what is happening on this screen in detail")
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "SCREEN_SUMMARIZE":
                message_queue.put({"type": "status", "value": "THINKING"})
                result = screen.read("Summarize the main content on this screen")
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "APP_OPEN":
                message_queue.put({"type": "status", "value": "THINKING"})
                subject = brain.extract_subject(query, intent)
                result = launcher.launch_app(subject)
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "CLIPBOARD_EXPLAIN":
                message_queue.put({"type": "status", "value": "THINKING"})
                result = brain.summary(clipboard.explain())
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "CLIPBOARD_TRANSLATE":
                message_queue.put({"type": "status", "value": "THINKING"})
                result = brain.summary(clipboard.translate())
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "VOLUME_UP":
                message_queue.put({"type": "status", "value": "THINKING"})
                value = brain.extract_number(query, intent)
                result = systemControl.volume_up(value if value else 10)
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "VOLUME_DOWN":
                message_queue.put({"type": "status", "value": "THINKING"})
                value = brain.extract_number(query, intent)
                result = systemControl.volume_down(value if value else 10)
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "BRIGHTNESS_SET":
                message_queue.put({"type": "status", "value": "THINKING"})
                value = brain.extract_number(query, intent)
                result = systemControl.set_brightness(value if value else 70)
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"}) 

            elif intent == "NOTE_ADD":
                message_queue.put({"type": "status", "value": "THINKING"})
                text = brain.extract_subject(query, intent)
                if text:
                    result = voice_note.add_note(text)
                else:
                    result = "I didn't catch what you wanted me to note down."
                    
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "NOTE_READ":
                message_queue.put({"type": "status", "value": "THINKING"})
                raw_num = brain.extract_number(query, intent)
                try:
                    number = int(raw_num) if raw_num else 1
                except ValueError:
                    number = 1
                    
                result = voice_note.read_note(number)
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "NOTE_CLEAR":
                message_queue.put({"type": "status", "value": "THINKING"})
                result = voice_note.clear_notes()
                message_queue.put({"type": "message", "sender": "NOVA", "text": result})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(result)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "SETTINGS":
                message_queue.put({"type": "status", "value": "THINKING"})
                dashboard.after(0, lambda: SettingsWindow(memory, voice_note, config))
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "WHITEBOARD":
                msg = "Opening hand tracking whiteboard canvas."
                message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(msg)
                gesture.open_whiteboard()
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "VOXEL_EDITOR":
                msg = "Launching 3D Voxel spatial environment."
                message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(msg)
                gesture.open_voxel_editor()
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "VIEW_MODEL":
                subject = brain.extract_subject(query, intent)
                clean_subject = subject.lower().replace("model", "").replace("3d", "").strip()
                if not clean_subject:
                    clean_subject = "generated_asset"
                    
                expected_filename = f"{clean_subject.replace(' ', '_')}.obj"
                
                local_path = os.path.abspath(os.path.join("data", "outputs", expected_filename))
                alt_path = os.path.abspath(os.path.join("skills", "model_gen", "outputs", expected_filename))
                
                target_path = local_path if os.path.exists(local_path) else alt_path
                
                if os.path.exists(target_path):
                    msg = f"Opening local 3D file structure for {clean_subject}."
                    message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(msg)
                    gesture.open_model(target_path)
                else:
                    msg = f"I could not locate a pre-cached file for {clean_subject}. Opening the default 3D canvas instead."
                    message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(msg)
                    gesture.open_sphere()
                    
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "GENERATE_MODEL":
                subject = brain.extract_subject(query, intent)
                msg = f"Submitting job generation token for {subject} to Shape-E cloud pipeline."
                message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(msg)
                message_queue.put({"type": "status", "value": "THINKING"})
                
                try:
                    downloaded_file = model_gen.generate(subject)
                    msg_success = f"Mesh asset created successfully. Initializing tracking matrix."
                    message_queue.put({"type": "message", "sender": "NOVA", "text": msg_success})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(msg_success)
                    gesture.open_model(downloaded_file)
                except TimeoutError as te:
                    msg_err = "The 3D generation request timed out. Please verify your remote Google Colab runtime session."
                    message_queue.put({"type": "message", "sender": "NOVA", "text": msg_err})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(msg_err)
                except Exception as e:
                    msg_err = "An internal processing exception halted the mesh asset workflow."
                    message_queue.put({"type": "message", "sender": "NOVA", "text": msg_err})
                    message_queue.put({"type": "status", "value": "SPEAKING"})
                    voice.speak(msg_err)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "DETECT_FACE":
                msg = "Activating camera frame recognition layers."
                message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(msg)
                message_queue.put({"type": "status", "value": "THINKING"})
                
                identities = facelink.identify()
                if isinstance(identities, list):
                    matches_str = ", ".join(identities)
                    msg_res = f"I recognize the following face outlines on the video sensor: {matches_str}."
                else:
                    msg_res = f"Face detection status update: {identities}."
                    
                message_queue.put({"type": "message", "sender": "NOVA", "text": msg_res})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(msg_res)
                message_queue.put({"type": "status", "value": "LISTENING"})

            elif intent == "CONVERSATION":
                memory.log("Shreyans", query)
                response = brain.ask(query)
                message_queue.put({"type": "message", "sender": "NOVA", "text": response})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(response)
                memory.log("NOVA", response)
                message_queue.put({"type": "status", "value": "LISTENING"})

            else:
                memory.log("Shreyans", query)
                response = brain.ask(query)
                message_queue.put({"type": "message", "sender": "NOVA", "text": response})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(response)
                memory.log("NOVA", response)
                message_queue.put({"type": "status", "value": "LISTENING"})

if __name__ == "__main__":
    message_queue = queue.Queue()
    input_queue = queue.Queue()
    app = Dashboard(message_queue, input_queue)
    
    nova_thread = threading.Thread(
        target=main, 
        args=(app, message_queue, input_queue),
        daemon=True
    )
    nova_thread.start()

    app.check_queue(message_queue)
    app.mainloop()
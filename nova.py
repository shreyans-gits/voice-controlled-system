import uvicorn
from core.server import app, initialize_server_bridges, _response_slots

import datetime
import time
import threading
from plyer import notification
import queue
import os
from concurrent.futures import ThreadPoolExecutor
from core.context import IntentContext

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


local_mic_muted = False

def greet():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return f"Good morning {config.USER_NAME}. NOVA online."
    elif hour < 18:
        return f"Good afternoon {config.USER_NAME}. NOVA online."
    else:
        return f"Good evening {config.USER_NAME}. NOVA online."


# --- MULTI-INTENT HANDLER ENGINE ---
# Every handler returns the response string so the network path can forward it.

def handle_weather(query, context, weather, message_queue, voice):
    weather_data = weather.getWeather()
    message_queue.put({"type": "message", "sender": "NOVA", "text": weather_data})
    message_queue.put({"type": "status", "value": "SPEAKING"})
    voice.speak(weather_data)
    context.set_result(weather_data)
    return weather_data


def handle_generate_model(item, query, context, model_gen, message_queue, voice):
    subject = item.get("subject")
    if not subject or subject == "null":
        subject = "generated_asset"

    msg = f"Submitting job generation token for {subject} to Shape-E cloud pipeline."
    message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
    message_queue.put({"type": "status", "value": "SPEAKING"})
    voice.speak(msg)
    message_queue.put({"type": "status", "value": "THINKING"})

    try:
        downloaded_file = model_gen.generate(subject)
        context.set_result(downloaded_file)
        return downloaded_file
    except TimeoutError:
        msg_err = "The 3D generation request timed out. Please verify your remote Google Colab runtime session."
        message_queue.put({"type": "message", "sender": "NOVA", "text": msg_err})
        voice.speak(msg_err)
        context.set_result(None)
        return msg_err
    except Exception as e:
        msg_err = f"An internal processing exception halted the mesh asset workflow: {e}"
        message_queue.put({"type": "message", "sender": "NOVA", "text": msg_err})
        voice.speak(msg_err)
        context.set_result(None)
        return msg_err


def handle_view_model(query, context, brain, gesture, message_queue, voice):
    local_path = context.get_result()
    if not local_path or not os.path.exists(str(local_path)):
        subject = brain.extract_subject(query, "VIEW_MODEL")
        clean_subject = subject.lower().replace("model", "").replace("3d", "").strip()
        if not clean_subject:
            clean_subject = "generated_asset"
        expected_filename = f"{clean_subject.replace(' ', '_')}.obj"
        path_a = os.path.abspath(os.path.join("data", "outputs", expected_filename))
        path_b = os.path.abspath(os.path.join("skills", "model_gen", "outputs", expected_filename))
        local_path = path_a if os.path.exists(path_a) else path_b

    if os.path.exists(str(local_path)):
        asset_name = os.path.basename(str(local_path)).replace(".obj", "").replace("_", " ")
        msg = f"Opening local 3D file structure for {asset_name}."
        message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
        voice.speak(msg)
        gesture.open_model(local_path)
        return msg
    else:
        msg = "I could not locate a pre-cached 3D file asset. Opening the default 3D canvas instead."
        message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
        voice.speak(msg)
        gesture.open_sphere()
        return msg


def handle_system_hardware(intent_name, message_queue, voice, system):
    if intent_name == "CPU":
        res = system.get_cpu()
    elif intent_name == "RAM":
        res = system.get_ram()
    else:
        res = system.get_battery()
    message_queue.put({"type": "message", "sender": "NOVA", "text": res})
    message_queue.put({"type": "status", "value": "SPEAKING"})
    voice.speak(res)
    return res


def handle_conversation(query, message_queue, voice, brain, memory):
    memory.log("Shreyans", query)
    response = brain.ask(query)
    message_queue.put({"type": "message", "sender": "NOVA", "text": response})
    message_queue.put({"type": "status", "value": "SPEAKING"})
    voice.speak(response)
    memory.log("NOVA", response)
    return response


def handle_app_launcher(query, brain, launcher, message_queue, voice):
    message_queue.put({"type": "status", "value": "THINKING"})
    subject = brain.extract_subject(query, "APP_OPEN")
    result = launcher.launch_app(subject)
    message_queue.put({"type": "message", "sender": "NOVA", "text": result})
    message_queue.put({"type": "status", "value": "SPEAKING"})
    voice.speak(result)
    return result


def handle_face_link(facelink, message_queue, voice):
    msg = "Activating camera frame recognition layers."
    message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
    voice.speak(msg)
    message_queue.put({"type": "status", "value": "THINKING"})

    identities = facelink.identify()
    if isinstance(identities, list):
        msg_res = f"I recognize the following face outlines on the video sensor: {', '.join(identities)}."
    else:
        msg_res = f"Face detection status update: {identities}."

    message_queue.put({"type": "message", "sender": "NOVA", "text": msg_res})
    message_queue.put({"type": "status", "value": "SPEAKING"})
    voice.speak(msg_res)
    return msg_res


def handle_search_modules(intent_name, query, brain, search, message_queue, voice):
    subject = brain.extract_subject(query, intent_name)
    if intent_name == "SEARCH":
        msg = f"Searching {subject}"
        message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
        voice.speak(msg)
        search.search(subject)
        return msg
    elif intent_name == "WATCH":
        msg = f"Searching {subject} on YouTube"
        message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
        voice.speak(msg)
        search.watch(subject)
        return msg
    elif intent_name == "WIKIPEDIA":
        voice.speak("Searching Wikipedia...")
        res = search.getWiki(subject)
        message_queue.put({"type": "message", "sender": "NOVA", "text": res})
        voice.speak(res)
        return res


def handle_news(news, message_queue, voice):
    titles = news.get_news()
    for i in titles:
        message_queue.put({"type": "message", "sender": "NOVA", "text": i})
        message_queue.put({"type": "status", "value": "SPEAKING"})
        voice.speak(i)
    return " | ".join(titles)


def handle_reminder(query, reminder, voice, message_queue):
    message_queue.put({"type": "message", "sender": "NOVA", "text": "What should I remind you about?"})
    voice.speak("What should I remind you about?")
    message_queue.put({"type": "status", "value": "LISTENING"})
    message = voice.listen()
    message_queue.put({"type": "message", "sender": "You", "text": message})
    message_queue.put({"type": "message", "sender": "NOVA", "text": "In how many minutes?"})
    voice.speak("In how many minutes?")
    message_queue.put({"type": "status", "value": "LISTENING"})
    time_str = voice.listen()
    message_queue.put({"type": "message", "sender": "You", "text": time_str})
    res = reminder.set_reminder(time_str, message)
    message_queue.put({"type": "message", "sender": "NOVA", "text": res})
    voice.speak(res)
    return res


def handle_whatsapp(query, wp, voice, message_queue, context, brain):
    pre_loaded_message = context.get_result()

    if pre_loaded_message:
        message = str(pre_loaded_message)
    else:
        message_queue.put({"type": "message", "sender": "NOVA", "text": "What is your message?"})
        voice.speak("What is your message?")
        message_queue.put({"type": "status", "value": "LISTENING"})
        message = voice.listen()
        message_queue.put({"type": "message", "sender": "You", "text": message})

    message = message + "\n\n_- This message was sent to you by NOVA_"

    subject = brain.extract_subject(query, "WHATSAPP") if "to" in query.lower() else ""
    name = subject.lower().strip()

    if not name:
        message_queue.put({"type": "message", "sender": "NOVA", "text": "To whom do you want to send the message?"})
        voice.speak("To whom do you want to send the message?")
        message_queue.put({"type": "status", "value": "LISTENING"})
        name = voice.listen().lower()
        message_queue.put({"type": "message", "sender": "You", "text": name})

    number = config.CONTACTS.get(name, "+916363466319")
    if name not in config.CONTACTS:
        msg = f"I couldn't find {name} in your contacts, so I'll send it to your default number."
        message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
        voice.speak(msg)

    res = wp.send_message(number, message)
    message_queue.put({"type": "message", "sender": "NOVA", "text": res})
    voice.speak(res)
    return res


def handle_spotify(intent_name, query, brain, spotify, message_queue, voice):
    if intent_name == "SPOTIFY_PLAY":
        subject = brain.extract_subject(query, intent_name)
        msg = f"Searching for {subject} on Spotify"
        message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
        voice.speak(msg)
        result = spotify.play(subject)
    elif intent_name == "SPOTIFY_PAUSE":
        result = spotify.pause()
    elif intent_name == "SPOTIFY_SKIP":
        result = spotify.next_track()
    message_queue.put({"type": "message", "sender": "NOVA", "text": result})
    voice.speak(result)
    return result


def handle_study_modules(intent_name, query, study, voice, message_queue):
    if intent_name == "POMODORO":
        try:
            mins = int(query.split("for")[1].split()[0])
            res = study.pomodoro(mins)
        except:
            res = study.pomodoro(25)
    elif intent_name == "SUMMARIZE":
        res = study.summarize_pdf()
    elif intent_name == "FLASHCARD":
        voice.speak("Give name of the topic")
        message_queue.put({"type": "status", "value": "LISTENING"})
        topic = voice.listen().lower()
        if topic:
            voice.speak(f"Generating flashcards for {topic}. Just a moment.")
            res = study.flashcard(topic)
        else:
            res = "I didn't catch the topic. Please try again."
    message_queue.put({"type": "message", "sender": "NOVA", "text": res})
    voice.speak(res)
    return res


def handle_vision_readers(intent_name, screen, message_queue, voice):
    message_queue.put({"type": "status", "value": "THINKING"})
    if intent_name == "SCREEN_READ":
        prompt = "Describe everything on this screen"
    elif intent_name == "SCREEN_EXPLAIN":
        prompt = "Explain what is happening on this screen in detail"
    else:
        prompt = "Summarize the main content on this screen"
    result = screen.read(prompt)
    message_queue.put({"type": "message", "sender": "NOVA", "text": result})
    voice.speak(result)
    return result


def handle_raw_clipboard_handoff(clipboard, message_queue, voice, context):
    raw_text = clipboard.clipGet()
    if not raw_text or not raw_text.strip():
        raw_text = "Empty clipboard content."
    voice.speak("Got your clipboard content.")
    context.set_result(raw_text)
    return raw_text


def handle_clipboard_skills(intent_name, clipboard, brain, message_queue, voice, context):
    raw_text = clipboard.explain() if intent_name == "CLIPBOARD_EXPLAIN" else clipboard.translate()
    result = brain.summary(raw_text)
    message_queue.put({"type": "message", "sender": "NOVA", "text": result})
    voice.speak(result)
    context.set_result(result)
    return result


def handle_hardware_control(intent_name, query, brain, systemControl, message_queue, voice):
    value = brain.extract_number(query, intent_name)
    if intent_name == "VOLUME_UP":
        result = systemControl.volume_up(value if value else 10)
    elif intent_name == "VOLUME_DOWN":
        result = systemControl.volume_down(value if value else 10)
    else:
        result = systemControl.set_brightness(value if value else 70)
    message_queue.put({"type": "message", "sender": "NOVA", "text": result})
    voice.speak(result)
    return result


def handle_voice_notes(intent_name, query, brain, voice_note, message_queue, voice):
    if intent_name == "NOTE_ADD":
        text = brain.extract_subject(query, intent_name)
        result = voice_note.add_note(text) if text else "I didn't catch what you wanted me to note down."
    elif intent_name == "NOTE_READ":
        raw_num = brain.extract_number(query, intent_name)
        try:
            number = int(raw_num) if raw_num else 1
        except ValueError:
            number = 1
        result = voice_note.read_note(number)
    else:
        result = voice_note.clear_notes()
    message_queue.put({"type": "message", "sender": "NOVA", "text": result})
    voice.speak(result)
    return result


def handle_static_skills(intent_name, gesture, message_queue, voice):
    if intent_name == "WHITEBOARD":
        msg = "Opening hand tracking whiteboard canvas."
        gesture.open_whiteboard()
    else:
        msg = "Launching 3D Voxel spatial environment."
        gesture.open_voxel_editor()
    message_queue.put({"type": "message", "sender": "NOVA", "text": msg})
    voice.speak(msg)
    return msg


def main(dashboard, message_queue, input_queue):
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
    print("[System Init] Initializing FaceLink Facial Recognition Databases...")
    import sys as _sys
    facelink = FaceLink()
    _sys.modules['__main__'].facelink = facelink
    model_gen = ModelGenModule()

    def reminder_checker():
        while True:
            alert = reminder.check_reminders()
            if alert:
                message_queue.put({"type": "message", "sender": "NOVA", "text": alert})
                message_queue.put({"type": "status", "value": "SPEAKING"})
                voice.speak(f"Reminder: {alert}")
                message_queue.put({"type": "status", "value": "LISTENING"})
                notification.notify(title="REMINDER!", message=alert, timeout=5)
            time.sleep(30)

    threading.Thread(target=reminder_checker, daemon=True).start()

    message_queue.put({"type": "message", "sender": "NOVA", "text": greet()})
    message_queue.put({"type": "status", "value": "SPEAKING"})
    voice.speak(greet())
    message_queue.put({"type": "status", "value": "LISTENING"})

    print("[System Engine] Launching asynchronous local web server...")
    initialize_server_bridges(input_queue)

    def run_web_server():
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

    threading.Thread(target=run_web_server, daemon=True).start()
    print("[System Engine] FastAPI server online at http://localhost:8000")

    global local_mic_muted
    local_mic_muted = False

    while True:
        message_queue.put({"type": "status", "value": "LISTENING"})
        query = ""
        current_request_context = {"origin": "local", "request_id": None}
        voice_result = [None]

        def do_listen():
            try:
                global local_mic_muted
                if local_mic_muted:
                    time.sleep(0.5)
                    voice_result[0] = ""
                    return
                voice_result[0] = voice.listen()
            except Exception as e:
                print(f"[Voice Thread Error] {e}")
                voice_result[0] = ""

        listen_thread = threading.Thread(target=do_listen, daemon=True)
        listen_thread.start()

        while listen_thread.is_alive():
            try:
                msg = input_queue.get_nowait()
                query = msg["text"]
                current_request_context["origin"] = msg.get("origin", "local")
                current_request_context["request_id"] = msg.get("request_id", None)
                break
            except queue.Empty:
                time.sleep(0.1)

        if not query:
            listen_thread.join()
            query = voice_result[0]

        if not query or not query.strip():
            continue

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
            intent_list = brain.get_intents(query)
            context = IntentContext()
            execution_outputs = []

            INTENT_HANDLERS = {
                "WEATHER": lambda item, q, ctx: handle_weather(q, ctx, weather, message_queue, voice),
                "GENERATE_MODEL": lambda item, q, ctx: handle_generate_model(item, q, ctx, model_gen, message_queue, voice),
                "VIEW_MODEL": lambda item, q, ctx: handle_view_model(q, ctx, brain, gesture, message_queue, voice),

                "CPU": lambda item, q, ctx: handle_system_hardware("CPU", message_queue, voice, system),
                "RAM": lambda item, q, ctx: handle_system_hardware("RAM", message_queue, voice, system),
                "BATTERY": lambda item, q, ctx: handle_system_hardware("BATTERY", message_queue, voice, system),
                "APP_OPEN": lambda item, q, ctx: handle_app_launcher(q, brain, launcher, message_queue, voice),
                "DETECT_FACE": lambda item, q, ctx: handle_face_link(facelink, message_queue, voice),
                "CONVERSATION": lambda item, q, ctx: handle_conversation(q, message_queue, voice, brain, memory),

                "SEARCH": lambda item, q, ctx: handle_search_modules("SEARCH", q, brain, search, message_queue, voice),
                "WATCH": lambda item, q, ctx: handle_search_modules("WATCH", q, brain, search, message_queue, voice),
                "WIKIPEDIA": lambda item, q, ctx: handle_search_modules("WIKIPEDIA", q, brain, search, message_queue, voice),

                "NEWS": lambda item, q, ctx: handle_news(news, message_queue, voice),
                "REMINDER": lambda item, q, ctx: handle_reminder(q, reminder, voice, message_queue),
                "WHATSAPP": lambda item, q, ctx: handle_whatsapp(q, wp, voice, message_queue, ctx, brain),

                "SPOTIFY_PLAY": lambda item, q, ctx: handle_spotify("SPOTIFY_PLAY", q, brain, spotify, message_queue, voice),
                "SPOTIFY_PAUSE": lambda item, q, ctx: handle_spotify("SPOTIFY_PAUSE", q, brain, spotify, message_queue, voice),
                "SPOTIFY_SKIP": lambda item, q, ctx: handle_spotify("SPOTIFY_SKIP", q, brain, spotify, message_queue, voice),

                "POMODORO": lambda item, q, ctx: handle_study_modules("POMODORO", q, study, voice, message_queue),
                "SUMMARIZE": lambda item, q, ctx: handle_study_modules("SUMMARIZE", q, study, voice, message_queue),
                "FLASHCARD": lambda item, q, ctx: handle_study_modules("FLASHCARD", q, study, voice, message_queue),

                "SCREEN_READ": lambda item, q, ctx: handle_vision_readers("SCREEN_READ", screen, message_queue, voice),
                "SCREEN_EXPLAIN": lambda item, q, ctx: handle_vision_readers("SCREEN_EXPLAIN", screen, message_queue, voice),
                "SCREEN_SUMMARIZE": lambda item, q, ctx: handle_vision_readers("SCREEN_SUMMARIZE", screen, message_queue, voice),

                "CLIPBOARD_EXPLAIN": lambda item, q, ctx: handle_clipboard_skills("CLIPBOARD_EXPLAIN", clipboard, brain, message_queue, voice, ctx),
                "CLIPBOARD_TRANSLATE": lambda item, q, ctx: handle_clipboard_skills("CLIPBOARD_TRANSLATE", clipboard, brain, message_queue, voice, ctx),
                "CLIPBOARD_GET": lambda item, q, ctx: handle_raw_clipboard_handoff(clipboard, message_queue, voice, ctx),

                "VOLUME_UP": lambda item, q, ctx: handle_hardware_control("VOLUME_UP", q, brain, systemControl, message_queue, voice),
                "VOLUME_DOWN": lambda item, q, ctx: handle_hardware_control("VOLUME_DOWN", q, brain, systemControl, message_queue, voice),
                "BRIGHTNESS_SET": lambda item, q, ctx: handle_hardware_control("BRIGHTNESS_SET", q, brain, systemControl, message_queue, voice),

                "NOTE_ADD": lambda item, q, ctx: handle_voice_notes("NOTE_ADD", q, brain, voice_note, message_queue, voice),
                "NOTE_READ": lambda item, q, ctx: handle_voice_notes("NOTE_READ", q, brain, voice_note, message_queue, voice),
                "NOTE_CLEAR": lambda item, q, ctx: handle_voice_notes("NOTE_CLEAR", q, brain, voice_note, message_queue, voice),

                "WHITEBOARD": lambda item, q, ctx: handle_static_skills("WHITEBOARD", gesture, message_queue, voice),
                "VOXEL_EDITOR": lambda item, q, ctx: handle_static_skills("VOXEL_EDITOR", gesture, message_queue, voice),
                "SETTINGS": lambda item, q, ctx: dashboard.after(0, lambda: SettingsWindow(memory, voice_note, config))
            }

            independent = [i for i in intent_list if not i.get("depends_on")]
            dependent = [i for i in intent_list if i.get("depends_on")]

            if independent:
                with ThreadPoolExecutor() as executor:
                    futures = {}
                    for item in independent:
                        intent_name = item["intent"]
                        if intent_name in INTENT_HANDLERS:
                            futures[intent_name] = executor.submit(INTENT_HANDLERS[intent_name], item, query, context)

                    for intent_name, future in futures.items():
                        try:
                            result = future.result()
                            if result and isinstance(result, str):
                                execution_outputs.append(result)
                        except Exception as thread_ex:
                            print(f"[Thread Error] {intent_name}: {thread_ex}")

            for item in dependent:
                intent_name = item["intent"]
                if intent_name in INTENT_HANDLERS:
                    result = INTENT_HANDLERS[intent_name](item, query, context)
                    if result and isinstance(result, str):
                        execution_outputs.append(result)

            # Build response payload for network callers
            response_payload = "\n".join(str(o) for o in execution_outputs if o).strip()
            if not response_payload:
                response_payload = "Done."

            # Dispatch back to phone app if this came from the network
            if current_request_context["origin"] == "network" and current_request_context["request_id"]:
                req_id = current_request_context["request_id"]
                if req_id in _response_slots:
                    _response_slots[req_id].put(response_payload)
                    print(f"[Network] Response dispatched for request: {req_id}")

            message_queue.put({"type": "status", "value": "LISTENING"})


if __name__ == "__main__":
    message_queue = queue.Queue()
    input_queue = queue.Queue()
    gui_dashboard = Dashboard(message_queue, input_queue)

    nova_thread = threading.Thread(
        target=main,
        args=(gui_dashboard, message_queue, input_queue),
        daemon=True
    )
    nova_thread.start()

    gui_dashboard.check_queue(message_queue)
    gui_dashboard.mainloop()

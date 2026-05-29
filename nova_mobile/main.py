import os
import time
import wave
import threading
import httpx
import numpy as np
import pyaudio

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.slider import MDSlider
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.uix.scrollview import ScrollView
from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView

from mobile_config import API_URL, LAPTOP_TAILSCALE_IP

class ChatBubble(MDCard):
    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.radius = [15, 15, 0, 15] if is_user else [15, 15, 15, 0]
        self.md_bg_color = (0, 0.25, 0.5, 0.9) if is_user else (0.14, 0.14, 0.18, 0.95)
        self.elevation = 1

        from kivy.core.window import Window
        self.width = min(dp(450), 0.75 * Window.width)
        self.pos_hint = {"right": 0.98} if is_user else {"left": 0.02}

        box = MDBoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(10), dp(12), dp(10)],
            size_hint=(1, None)
        )

        self.lbl = MDLabel(
            text=text,
            theme_text_color="Primary",
            font_style="Body1",
            size_hint=(1, None),
            halign="left",
            valign="top"
        )
        self.lbl.bind(width=lambda inst, val: setattr(inst, 'text_size', (val, None)))
        self.lbl.bind(texture_size=self._on_texture)

        box.add_widget(self.lbl)
        self.add_widget(box)
        self._box = box

    def _on_texture(self, instance, texture_size):
        instance.height = texture_size[1]
        self._box.height = texture_size[1] + dp(20)
        self.height = self._box.height


class DashboardScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance

        layout = MDBoxLayout(
            orientation="vertical",
            md_bg_color=(0.05, 0.05, 0.08, 1)
        )

        layout.add_widget(MDTopAppBar(
            title="N.O.V.A.",
            anchor_title="center",
            elevation=4,
            md_bg_color=(0.08, 0.08, 0.12, 1),
            right_action_items=[["cog", lambda x: self.app.switch_screen("settings")]]
        ))

        self.scroll_view = ScrollView(
            do_scroll_x=False,
            size_hint=(1, 1)
        )
        self.chat_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(12), dp(12), dp(12), dp(12)],
            size_hint_y=None
        )
        self.chat_container.bind(minimum_height=self.chat_container.setter('height'))
        self.scroll_view.add_widget(self.chat_container)
        layout.add_widget(self.scroll_view)

        self.add_bubble_to_ui(
            "System Core Connected. Hands-free audio monitoring online.",
            is_user=False
        )

        control_panel = MDBoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[dp(20), dp(12), dp(20), dp(20)],
            size_hint=(1, None),
            height=dp(160),
            md_bg_color=(0.08, 0.08, 0.12, 1)
        )

        self.status_lbl = MDLabel(
            text="MIC MUTED",
            halign="center",
            font_style="Button",
            theme_text_color="Error",
            size_hint_y=None,
            height=dp(30)
        )
        control_panel.add_widget(self.status_lbl)

        self.mic_btn = MDIconButton(
            icon="microphone-off",
            icon_size="52dp",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.18, 0.18, 0.22, 1),
            theme_icon_color="Custom",
            icon_color=(1, 0.3, 0.3, 1)
        )
        self.mic_btn.bind(on_release=self.toggle_microphone_state)
        control_panel.add_widget(self.mic_btn)

        layout.add_widget(control_panel)
        self.add_widget(layout)

    def add_bubble_to_ui(self, text, is_user=True):
        bubble = ChatBubble(text=text, is_user=is_user)
        bubble.size_hint_x = 0.78
        self.chat_container.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll_view, 'scroll_y', 0), 0.15)

    def toggle_microphone_state(self, instance):
        if self.app.is_muted:
            self.app.is_muted = False
            self.mic_btn.icon = "microphone"
            self.mic_btn.icon_color = (0, 0.8, 1, 1)
            self.mic_btn.md_bg_color = (0, 0.2, 0.4, 1)
            self.status_lbl.text = "LISTENING"
            self.status_lbl.theme_text_color = "Custom"
            self.status_lbl.text_color = (0, 0.8, 1, 1)
            self.app.sync_laptop_mic_state(mute=True)
            self.app.start_listening_loop()
        else:
            self.app.is_muted = True
            self.mic_btn.icon = "microphone-off"
            self.mic_btn.icon_color = (1, 0.3, 0.3, 1)
            self.mic_btn.md_bg_color = (0.18, 0.18, 0.22, 1)
            self.status_lbl.text = "MIC MUTED"
            self.status_lbl.theme_text_color = "Error"
            self.add_bubble_to_ui("Microphone paused.", is_user=False)
            self.app.sync_laptop_mic_state(mute=False)


class SettingsScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.current_contacts = {}

        layout = MDBoxLayout(orientation="vertical", md_bg_color=(0.05, 0.05, 0.08, 1))
        
        layout.add_widget(MDTopAppBar(
            title="System Settings Matrix",
            anchor_title="center",
            md_bg_color=(0.08, 0.08, 0.12, 1),
            left_action_items=[["arrow-left", lambda x: self.app.switch_screen("dashboard")]]
        ))

        scroll = ScrollView(do_scroll_x=False)
        form_layout = MDBoxLayout(orientation="vertical", spacing=dp(18), padding=dp(20), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        form_layout.add_widget(MDLabel(text="— Memory Core —", font_style="Subtitle2", theme_text_color="Custom", text_color=(0, 0.8, 1, 1), halign="center"))
        self.memory_box = MDTextField(text="Syncing core metadata...", multiline=True, size_hint_y=None, height=dp(100), readonly=True)
        form_layout.add_widget(self.memory_box)
        form_layout.add_widget(MDRaisedButton(text="WIPE MEMORY CORE", md_bg_color=(0.5, 0.1, 0.1, 1), pos_hint={"center_x": 0.5}, on_release=self.wipe_memory_remote))

        form_layout.add_widget(MDLabel(text="— Voice Notes —", font_style="Subtitle2", theme_text_color="Custom", text_color=(0, 0.8, 1, 1), halign="center"))
        form_layout.add_widget(MDRaisedButton(text="CLEAR ALL NOTES", md_bg_color=(0.2, 0.2, 0.25, 1), pos_hint={"center_x": 0.5}, on_release=self.clear_notes_remote))

        form_layout.add_widget(MDLabel(text="— Voice Speed —", font_style="Subtitle2", theme_text_color="Custom", text_color=(0, 0.8, 1, 1), halign="center"))
        self.speed_lbl = MDLabel(text="Speed: +0%", halign="center", font_style="Body2", theme_text_color="Secondary")
        form_layout.add_widget(self.speed_lbl)
        
        self.speed_slider = MDSlider(min=-50, max=50, value=0, step=1, size_hint_y=None, height=dp(30))
        self.speed_slider.bind(on_touch_up=self.on_slider_release)
        form_layout.add_widget(self.speed_slider)

        form_layout.add_widget(MDLabel(text="— Contact Directory —", font_style="Subtitle2", theme_text_color="Custom", text_color=(0, 0.8, 1, 1), halign="center"))
        
        add_contact_box = MDBoxLayout(orientation="horizontal", spacing=dp(5), size_hint_y=None, height=dp(50))
        self.new_name_input = MDTextField(hint_text="Name", size_hint_x=0.4)
        self.new_phone_input = MDTextField(hint_text="Phone Number", size_hint_x=0.4)
        add_btn = MDIconButton(icon="plus-box", icon_size="32dp", theme_icon_color="Custom", icon_color=(0, 0.8, 1, 1), on_release=self.add_contact_local)
        add_contact_box.add_widget(self.new_name_input)
        add_contact_box.add_widget(self.new_phone_input)
        add_contact_box.add_widget(add_btn)
        form_layout.add_widget(add_contact_box)

        self.contacts_list_ui = MDList()
        form_layout.add_widget(self.contacts_list_ui)

        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)
        
        self.on_enter = self.fetch_live_settings

    def fetch_live_settings(self):
        def run_fetch():
            try:
                response = httpx.get(f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/settings", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    Clock.schedule_once(lambda dt: self.update_ui_elements(data), 0)
            except Exception as e:
                print(f"[Fetch Error] Matrix sync failed: {e}")
        threading.Thread(target=run_fetch, daemon=True).start()

    def update_ui_elements(self, data):
        self.memory_box.text = data.get("memory_summary", "No summary logs available.")
        
        speed_str = data.get("voice_speed", "+0%")
        self.speed_lbl.text = f"Speed: {speed_str}"
        try:
            val = int(speed_str.replace("%", "").replace("+", ""))
            self.speed_slider.value = val
        except:
            self.speed_slider.value = 0

        self.current_contacts = data.get("contacts", {})
        self.rebuild_contacts_list_ui()

    def rebuild_contacts_list_ui(self):
        self.contacts_list_ui.clear_widgets()
        for name, phone in self.current_contacts.items():
            item = OneLineAvatarIconListItem(text=f"{name} : {phone}", theme_text_color="Primary")
            item.add_widget(IconLeftWidget(icon="account"))
            
            del_btn = IconRightWidget(icon="close-circle", theme_icon_color="Custom", icon_color=(0.8, 0.2, 0.2, 1))
            del_btn.bind(on_release=lambda x, n=name: self.delete_contact_remote(n))
            item.add_widget(del_btn)
            
            self.contacts_list_ui.add_widget(item)

    def on_slider_release(self, instance, touch):
        if instance.collide_point(*touch.pos):
            val = int(self.speed_slider.value)
            sign = "+" if val >= 0 else ""
            speed_str = f"{sign}{val}%"
            self.speed_lbl.text = f"Speed: {speed_str}"
            self.push_settings_update({"voice_speed": speed_str, "contacts": self.current_contacts})

    def add_contact_local(self, instance):
        name = self.new_name_input.text.strip().lower()
        phone = self.new_phone_input.text.strip()
        if name and phone:
            self.current_contacts[name] = phone
            self.new_name_input.text = ""
            self.new_phone_input.text = ""
            self.rebuild_contacts_list_ui()
            self.push_settings_update({"contacts": self.current_contacts})

    def delete_contact_remote(self, name_to_remove):
        if name_to_remove in self.current_contacts:
            del self.current_contacts[name_to_remove]
            self.rebuild_contacts_list_ui()
            self.push_settings_update({"contacts": self.current_contacts})

    def push_settings_update(self, payload):
        def run_push():
            try:
                httpx.post(f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/update_settings", json=payload, timeout=5.0)
            except Exception as e:
                print(f"[Push Error] Server write failed: {e}")
        threading.Thread(target=run_push, daemon=True).start()

    def wipe_memory_remote(self, instance):
        def run_wipe():
            try:
                httpx.post(f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/wipe_memory", timeout=5.0)
                Clock.schedule_once(lambda dt: setattr(self.memory_box, 'text', 'Memory cores wiped cleanly.'), 0)
            except Exception as e:
                print(e)
        threading.Thread(target=run_wipe, daemon=True).start()

    def clear_notes_remote(self, instance):
        def run_clear():
            try:
                url = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/update_settings"
                query_url = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/query"
                httpx.post(query_url, json={"text": "clear all notes"}, timeout=10.0)
            except Exception as e:
                print(e)
        threading.Thread(target=run_clear, daemon=True).start()


class NovaMobileApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"

        self.is_muted = True
        self._audio_thread_running = False
        self.pyaudio_instance = pyaudio.PyAudio()

        self.sm = ScreenManager()
        self.dashboard = DashboardScreen(self, name="dashboard")
        self.settings_screen = SettingsScreen(self, name="settings")

        self.sm.add_widget(self.dashboard)
        self.sm.add_widget(self.settings_screen)
        return self.sm

    def switch_screen(self, name):
        self.sm.current = name

    def start_listening_loop(self):
        if self._audio_thread_running:
            return
        self._audio_thread_running = True
        threading.Thread(target=self.continuous_audio_processor, daemon=True).start()

    def continuous_audio_processor(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        SILENCE_THRESHOLD = 500
        SILENCE_DURATION = 1.5

        if self.is_muted:
            self._audio_thread_running = False
            return

        try:
            stream = self.pyaudio_instance.open(
                format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK
            )
        except Exception as e:
            print(f"Mic open exception: {e}")
            self._audio_thread_running = False
            return

        audio_frames = []
        speaking_started = False
        silence_start_time = None

        print("[Audio Engine] 🟢 Mobile channel hot and listening...")

        while not self.is_muted:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_frames.append(data)
                amplitude = np.abs(np.frombuffer(data, dtype=np.int16)).mean()

                if amplitude > SILENCE_THRESHOLD:
                    if not speaking_started:
                        speaking_started = True
                        print("[Audio Engine] Voice signal intercepted.")
                    silence_start_time = None
                else:
                    if speaking_started:
                        if silence_start_time is None:
                            silence_start_time = time.time()
                        elif time.time() - silence_start_time > SILENCE_DURATION:
                            print("[Audio Engine] Silence limit reached. Preparing transmission...")
                            break
            except Exception as e:
                print(f"Buffer read error: {e}")
                break

        try:
            stream.stop_stream()
            stream.close()
        except:
            pass

        if audio_frames and speaking_started and not self.is_muted:
            unique_id = int(time.time())
            cache_path = f"mobile_input_{unique_id}.wav"
            with wave.open(cache_path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(self.pyaudio_instance.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(audio_frames))

            Clock.schedule_once(lambda dt: setattr(self.dashboard.status_lbl, 'text', "TRANSMITTING..."), 0)
            self._audio_thread_running = False
            self.transmit_audio_payload(cache_path)
        else:
            self._audio_thread_running = False
            Clock.schedule_once(lambda dt: self.reset_dashboard_state(), 0)

    def transmit_audio_payload(self, file_path):
        def async_post():
            try:
                url = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/process_audio"
                with open(file_path, "rb") as audio_file:
                    files = {"file": ("input.wav", audio_file, "audio/wav")}
                    response = httpx.post(url, files=files, timeout=45.0)

                if response.status_code == 200:
                    res_data = response.json()
                    user_speech = res_data.get('query', '')
                    nova_reply = res_data.get('text', '')

                    if user_speech:
                        Clock.schedule_once(
                            lambda dt: self.dashboard.add_bubble_to_ui(user_speech, is_user=True), 0
                        )
                    if nova_reply:
                        Clock.schedule_once(
                            lambda dt: self.dashboard.add_bubble_to_ui(nova_reply, is_user=False), 0
                        )
                        self.speak_response(nova_reply)
                else:
                    err = f"Server error: HTTP {response.status_code}"
                    Clock.schedule_once(
                        lambda dt: self.dashboard.add_bubble_to_ui(err, is_user=False), 0
                    )
            except Exception as e:
                err = f"Network error: {e}"
                Clock.schedule_once(
                    lambda dt: self.dashboard.add_bubble_to_ui(err, is_user=False), 0
                )
            finally:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
                Clock.schedule_once(lambda dt: self.reset_dashboard_state(), 1.0)

        threading.Thread(target=async_post, daemon=True).start()

    def speak_response(self, text):
        def do_speak():
            try:
                from kivy import platform
                if platform == 'android':
                    from plyer import tts
                    tts.speak(text)
                else:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.say(text)
                    engine.runAndWait()
            except Exception as e:
                print(f"[TTS Error] {e}")
        threading.Thread(target=do_speak, daemon=True).start()

    def reset_dashboard_state(self):
        if not self.is_muted:
            self.dashboard.status_lbl.text = "LISTENING"
            self.dashboard.status_lbl.text_color = (0, 0.8, 1, 1)
            self.sync_laptop_mic_state(mute=True)
            self.start_listening_loop()

    def sync_laptop_mic_state(self, mute):
        def async_sync():
            try:
                url = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/toggle_local_mic"
                httpx.post(url, json={"mute": mute}, timeout=3.0)
            except Exception as e:
                print(f"[Sync Warning] {e}")
        threading.Thread(target=async_sync, daemon=True).start()

    def on_stop(self):
        try:
            import requests
            requests.post(
                f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/toggle_local_mic",
                json={"mute": False},
                timeout=2.0
            )
        except:
            pass


if __name__ == "__main__":
    NovaMobileApp().run()
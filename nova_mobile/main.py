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

# Import secure absolute routing parameters
from mobile_config import API_URL, LAPTOP_TAILSCALE_IP

class DashboardScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        layout = MDBoxLayout(orientation="vertical")
        layout.add_widget(MDTopAppBar(
            title="NOVA Core Cockpit", 
            anchor_title="center", 
            elevation=4,
            right_action_items=[["cog", lambda x: self.app.switch_screen("settings")]]
        ))
        
        # Conversation Panel
        scroll = MDScrollView(do_scroll_x=False)
        self.chat_feed = MDLabel(
            text="[System Core Ready]\nMic Status: Muted by default.\nTap the array below to unlock hands-free communication.",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            padding=("10dp", "10dp")
        )
        self.chat_feed.bind(texture_size=self.chat_feed.setter('size'))
        scroll.add_widget(self.chat_feed)
        layout.add_widget(scroll)
        
        # Core Interface Controller: Giant Microphone Status Panel
        control_panel = MDBoxLayout(orientation="vertical", spacing="10dp", padding="20dp", size_hint_y=None, height="220dp")
        
        self.status_lbl = MDLabel(text="MIC MUTED", halign="center", font_style="H6", theme_text_color="Error")
        control_panel.add_widget(self.status_lbl)
        
        # Giant Toggle Button
        self.mic_btn = MDIconButton(
            icon="microphone-off",
            icon_size="70dp",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.2, 0.25, 1),
            theme_icon_color="Custom",
            icon_color=(1, 0.3, 0.3, 1)
        )
        self.mic_btn.bind(on_release=self.toggle_microphone_state)
        control_panel.add_widget(self.mic_btn)
        
        layout.add_widget(control_panel)
        self.add_widget(layout)

    def toggle_microphone_state(self, instance):
        if self.app.is_muted:
            # Unmute and spin up continuous automation logic
            self.app.is_muted = False
            self.mic_btn.icon = "microphone"
            self.mic_btn.icon_color = (0, 0.8, 1, 1)
            self.mic_btn.md_bg_color = (0, 0.2, 0.4, 1)
            self.status_lbl.text = "LISTENING (HANDS-FREE)"
            self.status_lbl.theme_text_color = "Custom"
            self.status_lbl.text_color = (0, 0.8, 1, 1)
            self.app.start_listening_loop()
        else:
            # Drop into hard standby (Football mode)
            self.app.is_muted = True
            self.mic_btn.icon = "microphone-off"
            self.mic_btn.icon_color = (1, 0.3, 0.3, 1)
            self.mic_btn.md_bg_color = (0.2, 0.2, 0.25, 1)
            self.status_lbl.text = "MIC MUTED"
            self.status_lbl.theme_text_color = "Error"
            self.chat_feed.text += "\n\n[Microphone arrays deactivated safely]"


class SettingsScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        layout = MDBoxLayout(orientation="vertical")
        layout.add_widget(MDTopAppBar(
            title="System Synchronization Profiles", 
            anchor_title="center", 
            left_action_items=[["arrow-left", lambda x: self.app.switch_screen("dashboard")]]
        ))
        
        content = MDBoxLayout(orientation="vertical", spacing="15dp", padding="20dp")
        
        # Memory Module Representation
        content.add_widget(MDLabel(text="— Memory Core —", font_style="Subtitle2", theme_text_color="Primary"))
        self.memory_box = MDTextField(text="Syncing metadata configurations...", multiline=True, size_hint_y=None, height="120dp", readonly=True)
        content.add_widget(self.memory_box)
        
        # Action Controllers
        content.add_widget(MDRaisedButton(text="WIPE SYSTEM MEMORY", md_bg_color=(0.7, 0.1, 0.1, 1), pos_hint={"center_x": 0.5}, on_release=self.wipe_memory_remote))
        
        layout.add_widget(content)
        self.add_widget(layout)
        self.on_enter = self.fetch_live_settings

    def fetch_live_settings(self):
        def run_fetch():
            try:
                response = httpx.get(f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/settings", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    Clock.schedule_once(lambda dt: self.update_fields(data), 0)
            except Exception as e:
                print(f"[Fetch Error] Sync block dropped: {e}")
        threading.Thread(target=run_fetch, daemon=True).start()

    def update_fields(self, data):
        self.memory_box.text = data.get("memory_summary", "No summary logs available.")

    def wipe_memory_remote(self, instance):
        def run_wipe():
            try:
                httpx.post(f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/wipe_memory", timeout=5.0)
                Clock.schedule_once(lambda dt: setattr(self.memory_box, 'text', 'Memory cores wiped.'), 0)
            except Exception as e:
                print(e)
        threading.Thread(target=run_wipe, daemon=True).start()


class NovaMobileApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        
        self.is_muted = True
        self.pyaudio_instance = pyaudio.PyAudio()
        
        self.sm = ScreenManager()
        self.dashboard = DashboardScreen(self, name="dashboard")
        self.settings = SettingsScreen(self, name="settings")
        
        self.sm.add_widget(self.dashboard)
        self.sm.add_widget(self.settings)
        return self.sm

    def switch_screen(self, name):
        self.sm.current = name

    def start_listening_loop(self):
        threading.Thread(target=self.continuous_audio_processor, daemon=True).start()

    def continuous_audio_processor(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024
        
        SILENCE_THRESHOLD = 500
        SILENCE_DURATION = 1.5
        
        while not self.is_muted:
            try:
                stream = self.pyaudio_instance.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self.dashboard.chat_feed, 'text', f"Mic open exception: {e}"), 0)
                break
                
            audio_frames = []
            speaking_started = False
            silence_start_time = None
            
            print("[Audio Engine] Hot channel active. Monitoring threshold signals...")
            
            while not self.is_muted:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    audio_frames.append(data)
                    
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    amplitude = np.abs(audio_data).mean()
                    
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
                                print("[Audio Engine] Silence limit reached. Preparing packet delivery...")
                                break
                except Exception as stream_err:
                    print(f"Buffer read crash: {stream_err}")
                    break
                    
            stream.stop_stream()
            stream.close()
            
            if audio_frames and speaking_started and not self.is_muted:
                cache_path = "mobile_input.wav"
                with wave.open(cache_path, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(self.pyaudio_instance.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(audio_frames))
                    
                Clock.schedule_once(lambda dt: setattr(self.dashboard.status_lbl, 'text', "TRANSMITTING..."), 0)
                self.transmit_audio_payload(cache_path)

    def transmit_audio_payload(self, file_path):
        def async_post():
            try:
                url = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/process_audio"
                with open(file_path, "rb") as audio_file:
                    files = {"file": ("input.wav", audio_file, "audio/wav")}
                    response = httpx.post(url, files=files, timeout=45.0)
                    
                if response.status_code == 200:
                    res_data = response.json()
                    text_update = f"\n\nYou: {res_data.get('query','')}\nNOVA: {res_data.get('text','')}"
                    Clock.schedule_once(lambda dt: self.update_chat_ui(text_update), 0)
                else:
                    Clock.schedule_once(lambda dt: self.update_chat_ui(f"\n\n[Server returned HTTP code {response.status_code}]"), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_chat_ui(f"\n\n[Bridge failure: {e}]"), 0)
            finally:
                Clock.schedule_once(lambda dt: self.reset_dashboard_state(), 0)
                
        threading.Thread(target=async_post, daemon=True).start()

    def update_chat_ui(self, text):
        self.dashboard.chat_feed.text += text

    def reset_dashboard_state(self):
        if not self.is_muted:
            self.dashboard.status_lbl.text = "LISTENING (HANDS-FREE)"
            self.dashboard.status_lbl.text_color = (0, 0.8, 1, 1)
            self.start_listening_loop()

if __name__ == "__main__":
    NovaMobileApp().run()
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

from mobile_config import API_URL, LAPTOP_TAILSCALE_IP

from kivymd.uix.card import MDCard
from kivy.uix.scrollview import ScrollView

class ChatBubble(MDCard):
    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.radius = [15, 15, 0, 15] if is_user else [15, 15, 15, 0]
        self.md_bg_color = (0, 0.25, 0.5, 0.9) if is_user else (0.14, 0.14, 0.18, 0.95)
        self.elevation = 1
        
        from kivy.core.window import Window
        self.width = min(450, 0.75 * Window.width)
        self.pos_hint = {"right": 0.98} if is_user else {"left": 0.02}
        
        box = MDBoxLayout(orientation="vertical", padding=15, size_hint=(1, 1))
        
        self.lbl = MDLabel(
            text=text,
            theme_text_color="Primary",
            font_style="Body1",
            size_hint_y=None,
            halign="left"
        )
        self.lbl.bind(width=lambda instance, val: setattr(instance, 'text_size', (val, None)))
        self.lbl.bind(texture_size=self.adjust_bubble_height)
        
        box.add_widget(self.lbl)
        self.add_widget(box)

    def adjust_bubble_height(self, instance, texture_size):
        self.height = texture_size[1] + 30


class DashboardScreen(Screen):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        
        layout = MDBoxLayout(orientation="vertical", md_bg_color=(0.05, 0.05, 0.08, 1))
        
        layout.add_widget(MDTopAppBar(
            title="NOVA Core Cockpit", 
            anchor_title="center", 
            elevation=4,
            md_bg_color=(0.08, 0.08, 0.12, 1),
            right_action_items=[["cog", lambda x: self.app.switch_screen("settings")]]
        ))
        
        self.scroll_view = ScrollView(do_scroll_x=False, size_hint=(1, 1))
        self.chat_container = MDBoxLayout(
            orientation="vertical", 
            spacing="12dp", 
            padding="15dp", 
            size_hint_y=None
        )
        self.chat_container.bind(minimum_height=self.chat_container.setter('height'))
        self.scroll_view.add_widget(self.chat_container)
        layout.add_widget(self.scroll_view)        
        self.add_bubble_to_ui("System Core Connected. Hands-free audio monitoring matrix online.", is_user=False)
        
        control_panel = MDBoxLayout(
            orientation="vertical", 
            spacing="8dp", 
            padding=["20dp", "10dp", "20dp", "20dp"], 
            size_hint_y=None, 
            height="180dp",
            md_bg_color=(0.08, 0.08, 0.12, 1)
        )
        
        self.status_lbl = MDLabel(
            text="MIC MUTED", 
            halign="center", 
            font_style="Button", 
            theme_text_color="Error"
        )
        control_panel.add_widget(self.status_lbl)
        
        self.mic_btn = MDIconButton(
            icon="microphone-off",
            icon_size="55dp",
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
        bubble.size_hint_x = 0.75 
        self.chat_container.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.scroll_view, 'scroll_y', 0), 0.1)

    def toggle_microphone_state(self, instance):
        if self.app.is_muted:
            self.app.is_muted = False
            self.mic_btn.icon = "microphone"
            self.mic_btn.icon_color = (0, 0.8, 1, 1)
            self.mic_btn.md_bg_color = (0, 0.2, 0.4, 1)
            self.status_lbl.text = "LISTENING (HANDS-FREE)"
            self.status_lbl.theme_text_color = "Custom"
            self.status_lbl.text_color = (0, 0.8, 1, 1)
            self.app.start_listening_loop()
            self.app.sync_laptop_mic_state(mute=True)
        else:
            self.app.is_muted = True
            self.mic_btn.icon = "microphone-off"
            self.mic_btn.icon_color = (1, 0.3, 0.3, 1)
            self.mic_btn.md_bg_color = (0.18, 0.18, 0.22, 1)
            self.status_lbl.text = "MIC MUTED"
            self.status_lbl.theme_text_color = "Error"
            self.add_bubble_to_ui("Microphone array paused.", is_user=False)
            self.app.sync_laptop_mic_state(mute=False)


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
                    user_speech = res_data.get('query', '')
                    nova_reply = res_data.get('text', '')
                    
                    if user_speech:
                        Clock.schedule_once(lambda dt: self.dashboard.add_bubble_to_ui(user_speech, is_user=True), 0)
                    if nova_reply:
                        Clock.schedule_once(lambda dt: self.dashboard.add_bubble_to_ui(nova_reply, is_user=False), 0)
                else:
                    err_msg = f"System Error: Server returned HTTP code {response.status_code}"
                    Clock.schedule_once(lambda dt: self.dashboard.add_bubble_to_ui(err_msg, is_user=False), 0)
            except Exception as e:
                error_string = str(e)
                ui_error_msg = f"Network Bridge Failure: {error_string}"
                Clock.schedule_once(lambda dt: self.dashboard.add_bubble_to_ui(ui_error_msg, is_user=False), 0)
            finally:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except: pass
                
                Clock.schedule_once(lambda dt: self.reset_dashboard_state(), 1.0)
                
        threading.Thread(target=async_post, daemon=True).start()

    def update_chat_ui(self, text):
        self.dashboard.chat_feed.text += text

    def reset_dashboard_state(self):
        if not self.is_muted:
            self.dashboard.status_lbl.text = "LISTENING (HANDS-FREE)"
            self.dashboard.status_lbl.text_color = (0, 0.8, 1, 1)
            self.start_listening_loop()

    def sync_laptop_mic_state(self, mute):
        def async_sync():
            try:
                url = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/toggle_local_mic"
                httpx.post(url, json={"mute": mute}, timeout=3.0)
            except Exception as e:
                print(f"[Sync Warning] Could not reach laptop mic gate: {e}")
                
        threading.Thread(target=async_sync, daemon=True).start()

    def on_stop(self):
        print("[Mobile App] Shutting down. Restoring laptop microphone arrays...")
        try:
            url = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/mobile/toggle_local_mic"
            import requests
            requests.post(url, json={"mute": False}, timeout=2.0)
        except Exception as e:
            print(f"[Exit Sync Failed] Could not restore laptop mic: {e}")

    def reset_dashboard_state(self):
        if not self.is_muted:
            self.dashboard.status_lbl.text = "LISTENING (HANDS-FREE)"
            self.dashboard.status_lbl.text_color = (0, 0.8, 1, 1)

            def delayed_restart(dt):
                if not self.is_muted:
                    self.start_listening_loop()
            Clock.schedule_once(delayed_restart, 0.3)

if __name__ == "__main__":
    NovaMobileApp().run()
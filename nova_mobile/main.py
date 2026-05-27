from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
import httpx
import threading
import mobile_config

LAPTOP_TAILSCALE_IP = mobile_config.LAPTOP_TAILSCALE_IP
API_URL = f"http://{LAPTOP_TAILSCALE_IP}:8000/api/query"

class MobilePortalLayout(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = "20dp"
        
        self.add_widget(MDTopAppBar(title="N.O.V.A. Mobile", anchor_title="center", elevation=4))
        
        content = MDBoxLayout(orientation="vertical", spacing="15dp", padding="20dp")
        
        self.response_label = MDLabel(
            text="System Status: Connected to Core Network\n\nWaiting for input command...",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1"
        )
        content.add_widget(self.response_label)
        
        self.input_field = MDTextField(
            hint_text="Type command or query...",
            helper_text="Example: check my ram system metrics",
            helper_text_mode="on_focus",
            line_color_focus=(0, 0.7, 1, 1)
        )
        content.add_widget(self.input_field)
        
        self.submit_btn = MDRaisedButton(
            text="TRANSMIT COMMAND",
            pos_hint={"center_x": 0.5},
            md_bg_color=(0, 0.5, 0.9, 1)
        )
        self.submit_btn.bind(on_release=self.send_command_async)
        content.add_widget(self.submit_btn)
        
        self.add_widget(content)

    def send_command_async(self, instance):
        """Fires the network request on a background thread so the phone UI never freezes."""
        query_text = self.input_field.text.strip()
        if not query_text:
            return
            
        self.response_label.text = "Transmitting to laptop core matrix..."
        self.input_field.text = ""
        
        threading.Thread(target=self.fire_rest_api, args=(query_text,), daemon=True).start()

    def fire_rest_api(self, text):
        try:
            response = httpx.post(API_URL, json={"text": text}, timeout=30.0)
            if response.status_code == 200:
                result_json = response.json()
                self.response_label.text = f"N.O.V.A. Response:\n\n{result_json.get('text', '')}"
            else:
                self.response_label.text = f"Network Server Error: Status Code {response.status_code}"
        except Exception as e:
            self.response_label.text = f"Failed to bridge to laptop core.\nCheck if Tailscale is active.\n\nError: {e}"

class NovaMobileApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark" # Keeps it looking like your dark-mode GUI dashboard
        self.theme_cls.primary_palette = "Blue"
        return MobilePortalLayout()

if __name__ == "__main__":
    NovaMobileApp().run()
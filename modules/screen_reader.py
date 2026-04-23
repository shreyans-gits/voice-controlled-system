import google.generativeai as genai
import config
from PIL import ImageGrab, Image
import os

class ScreenReaderModule:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_KEY)
        self.model = genai.GenerativeModel("gemini-3-flash-preview")

    def _capture(self):
        file_path = "temp_screen.png"
        screenshot = ImageGrab.grab()
        screenshot.save(file_path)
        return file_path

    def read(self,prompt = "What is on my screen"):
        path = self._capture()
        with Image.open(path) as img:
            response = self.model.generate_content([prompt, img])
            final_text = response.text
        if os.path.exists(path):
            os.remove(path)
        return final_text      
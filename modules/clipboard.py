import pyperclip as pc
from PIL import ImageGrab
import google.generativeai as genai
import config

class Clipboard:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_KEY)
        self.model = genai.GenerativeModel("gemini-3-flash-preview")

    def get(self):
        try:
            clipboard_image = ImageGrab.grabclipboard()
            if clipboard_image:
                if isinstance(clipboard_image, list):
                    from PIL import Image
                    clipboard_image = Image.open(clipboard_image[0])
                response = self.model.generate_content(["Explain this image : ", clipboard_image])
                return response.text
            text_content = pc.paste()
            if text_content and text_content.strip():
                return text_content
            
        except Exception as e:
            print(f"Clipboard error : {e}")
            return "Couldn't access clipboard"
        
        return "Couldn't access clipboard"
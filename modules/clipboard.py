import pyperclip as pc
from PIL import ImageGrab
import google.generativeai as genai
from groq import Groq
import config

class Clipboard:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_KEY)
        self.model = genai.GenerativeModel("gemini-3-flash-preview")

        self.clientG = Groq(api_key=config.GROQ_API_KEY)
        self.modelG = config.AI_MODEL

    def explain(self):
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
                translation_prompt = f"Translate the following text to English: {text_content}"
                return translation_prompt
            
        except Exception as e:
            print(f"Clipboard error : {e}")
            return "Couldn't access clipboard"
        
        return "Couldn't access clipboard"

    def translate(self):
        try:
            clipboard_image = ImageGrab.grabclipboard()
            if clipboard_image:
                if isinstance(clipboard_image, list):
                    from PIL import Image
                    clipboard_image = Image.open(clipboard_image[0])
                response = self.model.generate_content(["Translate the content of this image : ", clipboard_image])
                return response.text
            text_content = pc.paste()
            if text_content and text_content.strip():
                chat_completion = self.clientG.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional translator. Translate the user's text to English. "
                                    "Provide ONLY the translated text without quotes or explanations."
                        },
                        {
                            "role": "user",
                            "content": text_content,
                        }
                    ],
                    model=self.modelG,
                )
                return chat_completion.choices[0].message.content
            
        except Exception as e:
            print(f"Clipboard error : {e}")
            return "Couldn't access clipboard"
        
        return "Couldn't access clipboard"
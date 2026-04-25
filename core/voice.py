import speech_recognition as sr
import config
import pygame
import os
import tempfile
import asyncio
import edge_tts


class Voice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1

    def get_speed(self):
        import json
        if os.path.exists("settings.json"):
            with open("settings.json") as f:
                data = json.load(f)
                return data.get("voice_speed", "+0%")
        return "+0%"

    def speak(self, text):
        print(f"N.O.V.A.: {text}")

        async def generate():
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp.close()

            communicate = edge_tts.Communicate(
                text=text,
                voice=config.TTS_VOICE,
                rate=self.get_speed()
            )

            await communicate.save(temp.name)
            return temp.name

        file_path = asyncio.run(generate())

        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue

        pygame.mixer.quit()
        os.remove(file_path)

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)

        try:
            print("Recognizing...")
            query = self.recognizer.recognize_google(audio, language=config.TTS_LANGUAGE)
            print(f"You: {query}")
            return query.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            self.speak("Speech service is unavailable.")
            return ""
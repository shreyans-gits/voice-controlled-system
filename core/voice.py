import speech_recognition as sr
import config
from gtts import gTTS
import pygame
import os
import tempfile

class Voice:
    def __init__(self):
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1

    def speak(self, text):
        print(f"N.O.V.A.: {text}")
        temp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp.close()
        tts = gTTS(text=text, lang='en')
        tts.save(temp.name)
        pygame.mixer.init()
        pygame.mixer.music.load(temp.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.quit()
        os.remove(temp.name)

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)

        try:
            print("Recognizing...")
            query = self.recognizer.recognize_google(audio, language='en-in')
            print(f"You: {query}")
            return query.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            self.speak("Speech service is unavailable.")
            return ""
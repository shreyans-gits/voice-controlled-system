import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
TTS_Voice = os.getenv("TTS_Voice")
TTS_Lang = os.getenv("TTS_Lang")
City = os.getenv("CITY")
news = os.getenv("NEWS_API_KEY")

GROQ_API_KEY = API_KEY
ASSISTANT_NAME = "NOVA"
USER_NAME = "Shreyans"

# Voice settings
TTS_VOICE = TTS_Voice
TTS_LANGUAGE = TTS_Lang

# AI settings
AI_MODEL = "llama-3.3-70b-versatile"   # free and fast on Groq

# Weather settings
CITY = City

# NEWS
NEWS_KEY = news
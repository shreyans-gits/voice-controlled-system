import os
from dotenv import load_dotenv
import ast

load_dotenv()

API_KEY = os.getenv("API_KEY")
TTS_Voice = os.getenv("TTS_Voice")
TTS_Lang = os.getenv("TTS_Lang")
City = os.getenv("CITY")
news = os.getenv("NEWS_API_KEY")
contacts = os.getenv("contacts")
spotify_client_ID = os.getenv("spotify_client_id")
spotify_client_secret = os.getenv("spotify_client_secret")
spotify_uri = os.getenv("spotify_uri")

# BRAIN
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

# WHATSAPP
if contacts:
    CONTACTS = ast.literal_eval(contacts)
else:
    CONTACTS = {}

# SPOTIFY
SPOTIFY_ID = spotify_client_ID
SPOTIFY_SECRET = spotify_client_secret
SPOTIFY_URI = spotify_uri
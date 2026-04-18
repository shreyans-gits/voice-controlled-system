import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
GROQ_API_KEY = API_KEY
ASSISTANT_NAME = "NOVA"
USER_NAME = "Shreyans"

# Voice settings
VOICE_RATE = 200       # speed of speech
VOICE_VOLUME = 1.0     # 0.0 to 1.0

# AI settings
AI_MODEL = "llama-3.3-70b-versatile"   # free and fast on Groq
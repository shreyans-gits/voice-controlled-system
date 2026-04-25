# N.O.V.A.
### Neurally Optimized Voice Assistant

> A fully local, voice and text controlled AI desktop assistant built in Python. Talk to it, type to it — it understands what you want, routes to the right module, and responds through voice and a chat window.

---

## What is NOVA?

NOVA is a personal AI desktop assistant that runs entirely on your machine. It uses Groq's free API for lightning-fast AI responses, Microsoft Neural voices for natural speech output, and a clean CustomTkinter GUI. It remembers you across sessions, controls your system, reads your screen, and gets smarter the more you use it.

---

## Features

### Core
- **Voice + Text Input** — speak or type, NOVA handles both simultaneously
- **Natural Voice Output** — Microsoft Neural TTS via edge_tts
- **Intent Routing** — Groq classifies every query and routes to the right module automatically
- **Smart Memory** — at the end of every session, NOVA summarizes the conversation and remembers key facts about you across restarts
- **Threaded Architecture** — GUI never freezes, NOVA runs on a background thread

### Modules
| Module | What it does |
|---|---|
| Weather | Live weather via Open-Meteo, no API key needed |
| System | Battery, CPU, RAM stats via psutil |
| Search | Google, YouTube, Wikipedia |
| News | Top headlines via NewsAPI |
| Reminder | Timed reminders with desktop notifications |
| WhatsApp | Send WhatsApp messages via pywhatkit |
| Spotify | Play, pause, skip via Spotify API |
| Study | Pomodoro timer, PDF summarizer, flashcard generator |
| Screen Reader | Screenshot + Gemini Vision — NOVA reads and explains your screen |
| App Launcher | Open any app by voice |
| System Control | Volume and brightness control by voice |
| Voice Notes | Save and read back voice notes |
| Clipboard | Summarize or translate anything you copy |

### GUI
- Chat history with color coded messages
- Status indicator — IDLE / LISTENING / THINKING / SPEAKING
- Animated waveform when listening
- Text input with Enter to send
- System tray support — minimize to tray, NOVA keeps running
- Settings window — clear memory, clear notes, adjust voice speed, manage contacts

---

## Project Structure

```
NOVA/
├── core/
│   ├── brain.py        ← Groq AI, intent detection, subject extraction, memory summarization
│   ├── memory.py       ← Session logging, persistent memory across restarts
│   └── voice.py        ← speak() and listen()
├── gui/
│   ├── dashboard.py    ← Main CustomTkinter GUI
│   └── settings.py     ← Settings window
├── modules/
│   ├── app_launcher.py
│   ├── clipboard.py
│   ├── news.py
│   ├── reminder.py
│   ├── screen_reader.py
│   ├── search.py
│   ├── spotify.py
│   ├── study.py
│   ├── system_control.py
│   ├── system.py
│   ├── voice_note.py
│   ├── weather.py
│   └── whatsapp.py
├── Images/
│   └── NOVA_High.png
├── .env                ← created by setup.py, never committed
├── config.py
├── nova.py             ← entry point
└── setup.py            ← first time setup wizard
```

---

## Installation

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/NOVA.git
cd NOVA
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the setup wizard
```bash
python setup.py
```
This opens a GUI where you enter all your API keys and settings. It creates your `.env` file automatically and then closes itself.

### 4. Launch NOVA
```bash
python nova.py
```

---

## API Keys You Need

| Service | Where to get it | Required? |
|---|---|---|
| Groq | console.groq.com | ✅ Yes |
| Gemini | aistudio.google.com | ✅ Yes (Screen Reader + Clipboard) |
| NewsAPI | newsapi.org | ✅ Yes (News module) |
| Spotify | developer.spotify.com | ⚠️ Only for Spotify module |

All keys are entered through `setup.py` — you never need to edit any files manually.

---

## How It Works

```
You speak or type
→ voice.listen() or text input picked up
→ brain.get_intent() → one word like WEATHER or CONVERSATION
→ if needed, brain.extract_subject() → clean subject extracted
→ correct module called
→ result shown in chat window and spoken aloud
→ if CONVERSATION intent → logged to memory
→ on shutdown → session summarized by Groq and saved to memory.json
→ next startup → summary injected into system prompt so NOVA remembers you
```

---

## Voice Commands — Examples

```
"What's the weather like?"
"How's my battery?"
"Search for Python tutorials"
"Play some Drake on Spotify"
"Set a reminder in 10 minutes"
"Send a WhatsApp to Tani"
"What's on my screen?"
"Open Chrome"
"Volume up by 20"
"Set brightness to 50"
"Take a note"
"Summarize what I copied"
"Open settings"
"Clear your memory"
"Goodbye"
```

---

## Tech Stack

| Purpose | Tool |
|---|---|
| AI Brain | Groq API — Llama 3.3 70b |
| Voice Input | SpeechRecognition + Google Speech API |
| Voice Output | edge_tts + pygame |
| Screen Reading | Gemini Vision |
| GUI | CustomTkinter |
| Notifications | plyer |
| Audio Control | pycaw |
| Brightness Control | screen-brightness-control |
| Clipboard | pyperclip |

---

## Settings

Say "open settings" to access:
- **Memory** — view and clear NOVA's memory summary
- **Voice Speed** — adjust how fast NOVA speaks
- **Notes** — clear all saved voice notes
- **Contacts** — add, edit, or remove WhatsApp contacts

---

## Notes

- `memory.json` and `notes.json` are created automatically and ignored by git
- `.env` is never committed — always generated locally via `setup.py`
- NOVA minimizes to the system tray when you close the window — it keeps running in the background
- Say "goodbye", "quit", or "exit" to shut NOVA down properly so memory gets saved

---

## License

MIT License — do whatever you want with it.

---

*Built by Shreyans Sahu*

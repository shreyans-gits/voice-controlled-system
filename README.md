# N.O.V.A.
### Neurally Optimized Voice Assistant

> A fully local, voice and text controlled AI desktop assistant built in Python. Talk to it, type to it — NOVA understands intent, routes to the right module, responds through voice and a chat window, recognizes faces, renders 3D models, and executes multi-step tasks in a single sentence.

---

## What is NOVA?

NOVA is a personal AI desktop assistant that runs entirely on your machine. It uses Groq's free API for lightning-fast AI responses, Microsoft Neural voices for natural speech output, and a clean CustomTkinter GUI. It remembers you across sessions, controls your system, reads your screen, recognizes people by face, launches a full hand-gesture creative suite, generates 3D models from text on a remote Colab backend, and gets smarter the more you use it.

---

## Features

### Core
- **Voice + Text Input** — speak or type, NOVA handles both simultaneously
- **Natural Voice Output** — Microsoft Neural TTS via edge_tts
- **Multi-Intent Engine** — a single sentence can trigger multiple actions in sequence or parallel. "Generate a 3D apple and open it" → GENERATE_MODEL → VIEW_MODEL, chained automatically
- **Smart Memory** — at the end of every session, NOVA summarizes the conversation and remembers key facts about you across restarts
- **Threaded Architecture** — GUI never freezes, independent intents run in parallel via ThreadPoolExecutor, dependent intents execute sequentially with a shared context object

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

### Skills
| Skill | What it does |
|---|---|
| FaceLink | Real-time face recognition — NOVA identifies who is in front of the camera using enrolled embeddings. Supports single-frame identify mode and persistent live view |
| Gesture Suite | Full hand-tracking creative environment — launches Whiteboard (draw with your index finger), Voxel Editor (build 3D structures by pinching), and 3D Shapes viewer (sphere wireframe, OBJ/JSON model import, hand-rotate and scale) |
| ModelGen | Text-to-3D pipeline — submits a generation job to a Shap-E Colab notebook via Google Drive, polls for the result, downloads the OBJ to `data/outputs/`, and optionally opens it directly in the 3D viewer |

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
│   ├── brain.py        ← Groq AI, intent detection, multi-intent parsing, subject extraction
│   ├── context.py      ← IntentContext — shared state object passed between chained handlers
│   ├── memory.py       ← Session logging, persistent memory across restarts
│   └── voice.py        ← speak() and listen()
├── gui/
│   ├── dashboard.py    ← Main CustomTkinter GUI
│   └── settings.py     ← Settings window
├── modules/            ← One file per feature module
│   ├── weather.py
│   ├── system.py
│   ├── search.py
│   ├── news.py
│   ├── reminder.py
│   ├── whatsapp.py
│   ├── spotify.py
│   ├── study.py
│   ├── screen_reader.py
│   ├── app_launcher.py
│   ├── system_control.py
│   ├── voice_note.py
│   └── clipboard.py
├── skills/             ← Powerful integrations with their own runtimes
│   ├── facelink/
│   │   ├── facelink.py     ← FaceLink class — identify() and open_live()
│   │   ├── detector.py     ← HOG face detection via face_recognition
│   │   ├── embedder.py     ← 128-d face embedding extraction
│   │   ├── matcher.py      ← Cosine similarity matching against enrolled db
│   │   └── enrollment.py   ← Loads enrolled_faces.pkl
│   ├── gesture/
│   │   ├── gesture.py      ← GestureModule — subprocess launcher for app.py
│   │   ├── app.py          ← Gesture Lab entry point, accepts --mode --sub --file args
│   │   ├── HandTracker.py  ← MediaPipe hand landmark detection
│   │   ├── cubeeditor.py   ← Voxel editor — pinch to place, extend cubes
│   │   ├── whiteboard.py   ← Air canvas — draw with index finger
│   │   └── shapes3d.py     ← 3D wireframe viewer — sphere, JSON, OBJ via trimesh
│   └── model_gen/
│       ├── model_gen.py    ← ModelGenModule — wraps drive_client, returns file path
│       ├── generate.py     ← CLI tool for standalone generation jobs
│       ├── drive_client.py ← Google Drive upload/poll/download logic
│       └── outputs/        ← Generated OBJ files land here
├── data/
│   ├── enrolled_faces.pkl  ← FaceLink face database
│   ├── memory.json         ← Persistent session memory (auto-generated)
│   └── outputs/            ← NOVA's primary output directory for models
├── Images/
│   └── NOVA_High.png
├── .env                    ← Created by setup.py, never committed
├── config.py
├── nova.py                 ← Entry point
└── setup.py                ← First time setup wizard
```

---

## How It Works

```
You speak or type
→ brain.get_intents() → structured JSON list of intents with subjects and dependencies
→ independent intents (depends_on: null) → run in parallel via ThreadPoolExecutor
→ dependent intents (depends_on: "INTENT_NAME") → run sequentially after dependency completes
→ IntentContext object passes output between chained handlers
→ each handler calls its module, puts result in message_queue, speaks via voice
→ if CONVERSATION intent → logged to memory
→ on shutdown → session summarized by Groq and saved to memory.json
→ next startup → summary injected into system prompt so NOVA remembers you
```

### Multi-Intent Examples
```
"Check my CPU and tell me the weather"
→ [CPU, WEATHER] — both independent, run in parallel

"Generate a 3D castle and open it"
→ [GENERATE_MODEL(castle), VIEW_MODEL depends_on GENERATE_MODEL]
→ generates first, passes file path to viewer automatically

"Summarize what I copied and send it to Tani on WhatsApp"
→ [CLIPBOARD_EXPLAIN, WHATSAPP depends_on CLIPBOARD_EXPLAIN]
→ summarizes clipboard, passes summary as the WhatsApp message body
```

---

## Skills — Deep Dive

### FaceLink
Runs inside NOVA's process using the `face_recognition` library (dlib under the hood). Model files are resolved dynamically from the active venv's site-packages at startup via a module spoof.

- `identify()` — opens the webcam, grabs one frame, detects all faces, matches against the enrolled database, returns names
- `open_live()` — runs a persistent webcam loop in a daemon thread, draws bounding boxes and names on each face in real time

Enrollment is managed separately — faces are stored as 128-dimensional embeddings in `data/enrolled_faces.pkl`.

### Gesture Suite
The gesture skill launches `skills/gesture/app.py` as a non-blocking subprocess, passing arguments to set the initial mode:

```
gesture.open_whiteboard()       → app.py --mode whiteboard
gesture.open_voxel_editor()     → app.py --mode shapes3d --sub 0
gesture.open_model(path)        → app.py --mode shapes3d --sub 2 --file <path>
```

Inside `app.py`, the hand-tracking loop runs at 1280×720 via MediaPipe. Gesture controls:
- **Swipe down** — open sub-option panel
- **Index + middle finger cursor** — hover to select
- **Single index finger** — rotate model / draw on whiteboard
- **Pinch** — place cube / move model
- **Two-hand spread** — scale model

OBJ files are loaded via trimesh with automatic polygon decimation — meshes over 1200 faces are reduced dynamically to keep the CPU render loop smooth.

### ModelGen
Communicates with a Shap-E notebook running on Google Colab through Google Drive as a message bus:

```
NOVA calls model_gen.generate("castle")
→ sanitizes prompt → job_id = "castle"
→ uploads job file to Drive (prompt + format)
→ Colab notebook picks up the job, runs Shap-E, uploads result OBJ
→ model_gen polls Drive until result file appears (up to 300s timeout)
→ downloads OBJ to data/outputs/castle.obj
→ returns absolute file path to NOVA
→ if chained with VIEW_MODEL, gesture.open_model() receives the path automatically
```

---

## Voice Commands — Examples

```
"What's the weather like?"
"How's my battery?"
"Check my CPU and tell me the weather"        ← multi-intent, parallel
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
"Who is this?"                                 ← FaceLink identify
"Open face recognition"                        ← FaceLink live view
"Open whiteboard"                              ← Gesture Suite
"Open voxel editor"                            ← Gesture Suite
"Generate a 3D model of a fire hydrant"        ← ModelGen
"Generate a 3D castle and show it to me"       ← ModelGen → VIEW_MODEL chained
"Open settings"
"Goodbye"
```

---

## Installation

### 1. Clone the repo
```bash
git clone https://github.com/shreyans-gits/voice-controlled-system
cd NOVA
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the setup wizard
```bash
python setup.py
```
This opens a GUI where you enter all your API keys and settings. It creates your `.env` file automatically.

### 5. Launch NOVA
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
| Google Drive OAuth | console.cloud.google.com | ⚠️ Only for ModelGen skill |

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
| Face Recognition | face_recognition (dlib) |
| Hand Tracking | MediaPipe via HandTracker |
| 3D Mesh Loading | trimesh + fast_simplification |
| 3D Generation | Shap-E on Google Colab |
| Drive Communication | Google Drive API via drive_client |

---

## Notes

- `memory.json` and `notes.json` are created automatically and ignored by git
- `.env` is never committed — always generated locally via `setup.py`
- NOVA minimizes to the system tray when you close the window — it keeps running in the background
- Say "goodbye", "quit", or "exit" to shut NOVA down properly so memory gets saved
- The gesture suite requires a webcam and runs as a separate process so NOVA stays responsive while it's open
- ModelGen requires the Shap-E Colab notebook to be active and watching the Drive folder

---

## Roadmap

- [ ] FastAPI server — expose NOVA as a local API so the phone app can connect
- [ ] Tailscale — private network tunnel between phone and laptop
- [ ] NOVA Phone App — lightweight Android app, voice-only, sends queries to the laptop brain
- [ ] AR Overlay — ARCore overlays live NOVA responses on the real world via phone camera

---

*Built by Shreyans Sahu*

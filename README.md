# N.O.V.A.
### Neurally Optimized Voice Assistant

> A fully local, voice and text controlled AI desktop assistant built in Python. Talk to it, type to it — NOVA understands intent, routes to the right module, responds through voice and a chat window, recognizes faces, renders 3D models, executes multi-step tasks in a single sentence, and connects to your phone as a full bidirectional remote brain.

---

## What is NOVA?

NOVA is a personal AI desktop assistant that runs entirely on your machine. It uses Groq's free API for lightning-fast AI responses, Microsoft Neural voices for natural speech output, and a clean CustomTkinter GUI. It remembers you across sessions, controls your system, reads your screen, recognizes people by face, launches a full hand-gesture creative suite, generates 3D models from text on a remote Colab backend, and exposes itself as a FastAPI server so your phone can connect as a voice remote over Tailscale.

---

## Features

### Core
- **Voice + Text Input** — speak or type, NOVA handles both simultaneously
- **Natural Voice Output** — Microsoft Neural TTS via edge_tts
- **Multi-Intent Engine** — a single sentence triggers multiple actions in sequence or parallel. "Generate a 3D apple and open it" → GENERATE_MODEL → VIEW_MODEL, chained automatically
- **Smart Memory** — at the end of every session, NOVA summarizes the conversation and remembers key facts about you across restarts
- **Threaded Architecture** — GUI never freezes, independent intents run in parallel via ThreadPoolExecutor, dependent intents execute sequentially with a shared context object
- **FastAPI Server** — built into nova.py, starts automatically, exposes NOVA as a local API on port 8000

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
| FaceLink | Real-time face recognition — NOVA identifies who is in front of the camera using enrolled embeddings. Supports single-frame identify mode, persistent live view, and live overlay on the phone's reverse camera stream |
| Gesture Suite | Full hand-tracking creative environment — launches Whiteboard (draw with your index finger), Voxel Editor (build 3D structures by pinching), and 3D Shapes viewer (sphere wireframe, OBJ/JSON model import, hand-rotate and scale) |
| ModelGen | Text-to-3D pipeline — submits a generation job to a Shap-E Colab notebook via Google Drive, polls for the result, downloads the OBJ to `data/outputs/`, and optionally opens it directly in the 3D viewer |

### NOVA Desktop-Phone Link
A companion Android app that turns your phone into a bidirectional remote for NOVA over Tailscale.

| Feature | What it does |
|---|---|
| Hands-Free Voice | Phone mic captures speech, sends WAV to laptop, NOVA processes and responds, phone speaks reply via TTS |
| Acoustic Echo Isolation | Automatically mutes/unmutes laptop mic based on phone transmission state — no feedback loops |
| Laptop Webcam Stream | Live MJPEG stream from laptop webcam rendered on phone in landscape mode |
| Phone Camera → Laptop | Reverse stream — phone camera feeds frames to laptop browser in real time with FaceLink overlay |
| FaceLink on Phone | Point phone camera at people — face detection and identification overlaid live on browser view |
| Camera Flip | Toggle between front and rear camera during reverse stream |
| Settings Sync | View/wipe memory, adjust voice speed, manage WhatsApp contacts, clear notes — all from phone |

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
│   ├── server.py       ← FastAPI server — REST API, audio pipeline, video streams, settings sync
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
│   │   ├── facelink.py         ← FaceLink class — identify(), open_live(), detect_and_identify_frame()
│   │   ├── detector.py         ← HOG face detection via face_recognition
│   │   ├── embedder.py         ← 128-d face embedding extraction
│   │   ├── matcher.py          ← Cosine similarity matching against enrolled db
│   │   └── enrollment.py       ← Loads enrolled_faces.pkl
│   ├── gesture/
│   │   ├── gesture.py          ← GestureModule — subprocess launcher for app.py
│   │   ├── app.py              ← Gesture Lab entry point, accepts --mode --sub --file args
│   │   ├── HandTracker.py      ← MediaPipe hand landmark detection
│   │   ├── cubeeditor.py       ← Voxel editor — pinch to place, extend cubes
│   │   ├── whiteboard.py       ← Air canvas — draw with index finger
│   │   └── shapes3d.py         ← 3D wireframe viewer — sphere, JSON, OBJ via trimesh
│   └── model_gen/
│       ├── model_gen.py        ← ModelGenModule — wraps drive_client, returns file path
│       ├── generate.py         ← CLI tool for standalone generation jobs
│       ├── drive_client.py     ← Google Drive upload/poll/download logic
│       └── outputs/            ← Generated OBJ files land here
├── phone_app/                  ← NOVA Desktop-Phone Link (KivyMD Android app)
│   ├── main.py                 ← App entry point — dashboard, webcam, settings screens
│   ├── mobile_config.py        ← Tailscale IP config (gitignored)
│   ├── mobile_config.example.py← Template for mobile_config.py
│   ├── buildozer.spec          ← Android APK build config
│   └── logo.png
├── data/
│   ├── enrolled_faces.pkl      ← FaceLink face database
│   ├── memory.json             ← Persistent session memory (auto-generated)
│   └── outputs/                ← NOVA's primary output directory for models
├── Images/
│   └── NOVA_High.png
├── .env                        ← Created by setup.py, never committed
├── config.py
├── nova.py                     ← Entry point — starts NOVA + FastAPI server
└── setup.py                    ← First time setup wizard
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

### Phone Link Flow
```
Phone mic captures speech
→ WAV payload sent to laptop FastAPI server (/api/mobile/process_audio)
→ server transcribes audio via Google Speech API
→ query injected into NOVA's input queue
→ NOVA processes intent, generates response
→ response returned to phone over HTTP
→ phone speaks reply via TTS + shows in chat
→ laptop mic automatically restored after exchange
```

---

## Skills — Deep Dive

### FaceLink
Runs inside NOVA's process using the `face_recognition` library (dlib under the hood). Model files are resolved dynamically from the active venv's site-packages at startup via a module spoof.

- `identify()` — opens the webcam, grabs one frame, detects all faces, matches against the enrolled database, returns names
- `open_live()` — runs a persistent webcam loop in a daemon thread, draws bounding boxes and names on each face in real time
- `detect_and_identify_frame(frame)` — takes an externally provided OpenCV frame, runs detection and matching, returns `(location, name)` tuples — used by the phone reverse stream pipeline

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

### NOVA Desktop-Phone Link — Deep Dive

The phone app communicates with the laptop over Tailscale via the FastAPI server built into `nova.py`.

**Audio pipeline:**
The phone captures raw audio via PyAudio, detects speech using amplitude-based silence detection, compiles a WAV file, and POSTs it to `/api/mobile/process_audio`. The server transcribes it using Google Speech API and injects the query into NOVA's input queue. The response is returned synchronously and spoken aloud on the phone.

**Video streams:**
- Laptop → Phone: `/api/mobile/video_feed` streams MJPEG frames from the laptop webcam. The phone parses the boundary bytes, decodes JPEG frames, and renders them as Kivy textures.
- Phone → Laptop: The phone captures frames via OpenCV, encodes them as JPEG, and POSTs them to `/api/mobile/upload_frame`. The server runs FaceLink's `detect_and_identify_frame()` on each frame, overlays bounding boxes and names, and re-encodes for browser streaming at `/mobile_camera`.

**Settings sync:**
All settings reads and writes go through `/api/mobile/settings` and `/api/mobile/update_settings`. Contact changes write directly to the `.env` file on the laptop.

---

## Phone App Setup

### 1. Configure Tailscale IP
Copy `mobile_config.example.py` to `mobile_config.py` and fill in your laptop's Tailscale IP:
```python
LAPTOP_TAILSCALE_IP = "100.x.x.x"
```

### 2. Build the APK
```bash
cd phone_app
buildozer android debug
```
First build takes 20-30 minutes. The APK appears in `bin/`.

### 3. Install on phone
```bash
buildozer android deploy run
```
Or copy the APK from `bin/` and install manually.

### 4. Connect
Make sure both laptop and phone are on the same Tailscale network. Run `python nova.py` on the laptop — the FastAPI server starts automatically on port 8000.

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
| REST API Server | FastAPI + uvicorn |
| Phone App | KivyMD (Android) |
| Phone Networking | Tailscale + httpx |
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
- `mobile_config.py` is never committed — copy from `mobile_config.example.py`
- NOVA minimizes to the system tray when you close the window — it keeps running in the background
- Say "goodbye", "quit", or "exit" to shut NOVA down properly so memory gets saved
- The gesture suite requires a webcam and runs as a separate process so NOVA stays responsive
- ModelGen requires the Shap-E Colab notebook to be active and watching the Drive folder
- The FastAPI server starts automatically with `nova.py` — no separate process needed

---

## Roadmap

- [ ] NOVA Mobile — a proper Android assistant app that controls the phone itself (Spotify on phone, phone contacts, notifications)
- [ ] AR Overlay — ARCore overlays live NOVA responses on the real world via phone camera
- [ ] SentinelAI — multimodal awareness system (face expressions, pose, audio spikes, presence detection)
- [ ] Wake word on phone — hands-free trigger within active mic session

---

*Built by Shreyans Sahu*

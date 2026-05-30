from fastapi import FastAPI, BackgroundTasks, APIRouter, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import pydantic
import queue
import cv2
import json
import os
import numpy as np
import sys

app = FastAPI(title="N.O.V.A. Core API Layer", version="1.0.0")
router = APIRouter(prefix="/api/mobile")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_input_queue = None
_response_slots = {}

class QueryRequest(pydantic.BaseModel):
    text: str

class SettingsUpdateRequest(pydantic.BaseModel):
    voice_speed: str = None
    contacts: dict = None

def initialize_server_bridges(input_queue):
    global _input_queue
    _input_queue = input_queue

@app.post("/api/query")
async def handle_network_query(payload: QueryRequest, background_tasks: BackgroundTasks):
    global _input_queue, _response_slots
    clean_text = payload.text.strip()
    if not clean_text:
        return {"status": "error", "sender": "NOVA", "text": "Empty query received."}
        
    print(f"[Server API] Received external network command: '{clean_text}'")
    
    import uuid
    request_id = str(uuid.uuid4())
    response_queue = queue.Queue()
    _response_slots[request_id] = response_queue
    
    _input_queue.put({"text": clean_text, "origin": "network", "request_id": request_id})

    try:
        import asyncio
        loop = asyncio.get_event_loop()
        final_response = await loop.run_in_executor(None, lambda: response_queue.get(timeout=45.0))
        return {"status": "success", "sender": "NOVA", "text": final_response}
    except queue.Empty:
        return {"status": "timeout", "sender": "NOVA", "text": "Execution task took too long to complete."}
    finally:
        if request_id in _response_slots:
            del _response_slots[request_id]

def dispatch_network_response(request_id, response_text):
    global _response_slots
    if request_id in _response_slots:
        _response_slots[request_id].put(response_text)

# MOBILE DASHBOARD & CONFIGURATION ENDPOINTS

camera_active = False

@router.get("/settings")
def get_current_settings():
    from core.memory import Memory
    import config
    
    memory = Memory()
    voice_speed = "+0%"
    if os.path.exists("settings.json"):
        with open("settings.json") as f:
            try: voice_speed = json.load(f).get("voice_speed", "+0%")
            except: pass

    return {
        "memory_summary": memory.summary,
        "voice_speed": voice_speed,
        "contacts": config.CONTACTS
    }

@router.post("/update_settings")
async def update_settings(payload: SettingsUpdateRequest):
    import config
    
    if payload.voice_speed is not None:
        with open("settings.json", "w") as f:
            json.dump({"voice_speed": payload.voice_speed}, f)
            
    if payload.contacts is not None:
        config.CONTACTS = payload.contacts
        env_path = ".env"
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
            with open(env_path, 'w') as f:
                for line in lines:
                    if line.startswith("contacts"):
                        f.write(f"contacts = {json.dumps(payload.contacts)}\n")
                    else:
                        f.write(line)
                        
    return {"status": "success", "message": "System settings synchronized."}

@router.post("/wipe_memory")
def wipe_system_memory():
    from core.memory import Memory
    memory = Memory()
    memory.clear()
    return {"status": "success", "message": "Memory cores cleared."}

@router.post("/toggle_local_mic")
async def toggle_local_mic(payload: dict):
    import sys
    main_module = sys.modules.get('__main__')
    
    mute_status = payload.get("mute", False)
    if main_module and hasattr(main_module, "local_mic_muted"):
        main_module.local_mic_muted = mute_status
        state_str = "MUTED" if mute_status else "ACTIVE"
        print(f"[System Core] Laptop hardware mic state switched to: {state_str}")
        return {"status": "success", "local_mic_muted": mute_status}
        
    return {"status": "error", "message": "Core lifecycle reference unavailable."}

# MOBILE REMOTE AUDIO PROCESSING PIPELINE

@router.post("/process_audio")
async def process_mobile_audio(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    global _input_queue, _response_slots
    try:
        temp_audio_path = f"data/outputs/mobile_incoming_{file.filename}"
        os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
        with open(temp_audio_path, "wb") as f:
            f.write(await file.read())
            
        import speech_recognition as sr
        import config
        from core.voice import Voice
        
        voice_engine = Voice()
        transcribed_query = ""

        if os.path.exists(temp_audio_path):
            with sr.AudioFile(temp_audio_path) as source:
                print("[Server STT] Extracting audio data from mobile payload cache...")
                audio_data = voice_engine.recognizer.record(source)
                try:
                    transcribed_query = voice_engine.recognizer.recognize_google(
                        audio_data, 
                        language=config.TTS_LANGUAGE
                    ).lower()
                    print(f"[Server STT] Transcribed Mobile Input: '{transcribed_query}'")
                except sr.UnknownValueError:
                    print("[Server STT] Google engine could not decipher audio data matrix.")
                except sr.RequestError as e:
                    print(f"[Server STT] API service connection drop: {e}")

        try: os.remove(temp_audio_path)
        except: pass
            
        if not transcribed_query or not transcribed_query.strip():
            return {"status": "error", "text": "Could not decipher speech inputs."}
            
        import uuid
        request_id = str(uuid.uuid4())
        response_queue = queue.Queue()
        _response_slots[request_id] = response_queue
        
        _input_queue.put({"text": transcribed_query, "origin": "network", "request_id": request_id})
        
        import asyncio
        loop = asyncio.get_event_loop()
        final_response = await loop.run_in_executor(None, lambda: response_queue.get(timeout=45.0))
        return {"status": "success", "query": transcribed_query, "text": final_response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio thread pipeline failure: {e}")

# WEBCAM REAL-TIME MOTION JPEG STREAM GENERATION

def generate_webcam_frames():
    global camera_active
    cap = cv2.VideoCapture(0)
    
    while camera_active:
        success, frame = cap.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
    cap.release()

@router.get("/video_feed")
def stream_video_feed():
    global camera_active
    camera_active = True
    return StreamingResponse(generate_webcam_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.post("/stop_feed")
def stop_video_feed():
    global camera_active
    camera_active = False
    return {"status": "Camera deactivated"}


import webbrowser
from fastapi import Request
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio

current_mobile_frame = None

@router.post("/start_reverse_stream")
async def start_reverse_stream():
    print("[Server Pipeline] Phone camera request verified. Launching browser canvas...")
    webbrowser.open("http://localhost:8000/mobile_camera")
    return {"status": "success", "message": "Browser tab opened automatically."}

@router.post("/upload_frame")
async def upload_mobile_frame(request: Request):
    global current_mobile_frame, reverse_stream_active
    if not reverse_stream_active:
        return {"status": "ignored"}
    img_bytes = await request.body()
    
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is not None:
            main_module = sys.modules.get('__main__')
            
            if main_module and hasattr(main_module, 'facelink'):
                face_locations = main_module.facelink.face_locations(frame)
                
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 229, 0), 2) # BGR Cyan/Blue highlight
                    
                    cv2.putText(frame, "TRACKING STATE: VERIFIED USER", (left, top - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 229, 0), 2)
            
            _, encoded_img = cv2.imencode('.jpg', frame)
            current_mobile_frame = encoded_img.tobytes()
        else:
            current_mobile_frame = img_bytes
            
    except Exception as cv_err:
        print(f"[FaceLink Pipeline Error] Frame scan aborted: {cv_err}")
        current_mobile_frame = img_bytes

    return {"status": "received"}

@router.get("/stream_browser_view")
async def stream_browser_view():
    async def frame_generator():
        global current_mobile_frame
        while True:
            if current_mobile_frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + current_mobile_frame + b'\r\n')
            await asyncio.sleep(0.033)

    return StreamingResponse(frame_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/mobile_camera", response_class=HTMLResponse)
async def mobile_camera_page():
    return """
    <html>
        <head>
            <title>NOVA Roaming Eye Feed</title>
            <style>
                body { margin: 0; background: #050508; display: flex; justify-content: center; align-items: center; height: 100vh; color: #00e5ff; font-family: monospace; }
                .container { text-align: center; }
                img { border: 2px solid #005588; border-radius: 12px; max-width: 90vw; max-height: 80vh; box-shadow: 0 0 20px rgba(0,229,255,0.2); }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>[ LIVE PORTAL - ROAMING MOBILE EYE ]</h2>
                <img src="/api/mobile/stream_browser_view" />
            </div>
        </body>
    </html>
    """

app.include_router(router)
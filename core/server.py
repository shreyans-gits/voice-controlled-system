import pydantic
from fastapi import FastAPI, BackgroundTasks, APIRouter, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import queue
import cv2
import json
import os

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

# MOBILE REMOTE AUDIO PROCESSING PIPELINE

@router.post("/process_audio")
async def process_mobile_audio(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Receives voice recordings from phone mic, transcribes, and runs via intent graph."""
    global _input_queue, _response_slots
    try:
        temp_audio_path = f"data/outputs/mobile_incoming_{file.filename}"
        os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
        with open(temp_audio_path, "wb") as f:
            f.write(await file.read())
            
        from core.voice import Voice
        voice_engine = Voice()

        if hasattr(voice_engine, "transcribe_file"):
            transcribed_query = voice_engine.transcribe_file(temp_audio_path)
        else:
            transcribed_query = "" 
            
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

app.include_router(router)
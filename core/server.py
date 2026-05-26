import pydantic
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import queue

app = FastAPI(title="N.O.V.A. Core API Layer", version="1.0.0")

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
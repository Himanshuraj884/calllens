import os, tempfile, time, uuid
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import llm, metrics, store
from rag import Playbook
from transcribe import transcribe_audio

BASE = Path(__file__).parent
MAX_BYTES = 50_000_000
ADMIN_TOKEN = os.getenv("CALLLENS_ADMIN_TOKEN", "")
app = FastAPI(title="CallLens")
store.init()
playbook = Playbook(BASE / "playbook.md")

class Ask(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    user_id: str = "anon"

class Feedback(BaseModel):
    rating: int = Field(ge=1, le=5)
    confirmed: list[Optional[bool]] = []
    comment: str = ""

class Event(BaseModel):
    user_id: str
    call_id: str = ""
    name: str

@app.post("/api/calls")
def upload_call(file: UploadFile = File(...), user_id: str = Form("")):
    # Sync on purpose: runs in a worker thread so slow STT/LLM calls don't block other requests.
    t0 = time.time()
    user_id = user_id.strip()[:60]
    if not user_id or user_id.lower() == "anon":
        raise HTTPException(400, "Enter your name so pilot metrics are attributed correctly.")
    data = file.file.read(MAX_BYTES + 1)
    if not data or len(data) > MAX_BYTES:
        raise HTTPException(400, "Upload a non-empty file under 50 MB.")
    suffix = Path(file.filename or "").suffix.lower()
    stt_seconds = 0.0
    if suffix in {".txt", ".md"}:
        transcript = data.decode("utf-8", errors="ignore")
    elif suffix in {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4", ".webm"}:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(data); path = tmp.name
        try:
            s = time.time()
            transcript = transcribe_audio(path)
            stt_seconds = time.time() - s
        except RuntimeError as e:
            raise HTTPException(500, str(e))
        finally:
            os.unlink(path)
    else:
        raise HTTPException(400, "Use audio (.wav .mp3 .m4a) or a .txt transcript.")
    if len(transcript.strip()) < 40:
        raise HTTPException(400, "Transcript is too short to analyse.")
    result, mode = llm.analyze(transcript)
    call = {"id": uuid.uuid4().hex[:10], "user_id": user_id, "filename": file.filename,
            "transcript": transcript, "result": result, "mode": mode,
            "stt_seconds": round(stt_seconds, 2), "total_seconds": round(time.time() - t0, 2)}
    store.save_call(call)
    store.log_event(user_id, call["id"], "upload")
    return call

@app.get("/api/calls/{call_id}")
def get_call(call_id: str):
    call = store.get_call(call_id)
    if not call:
        raise HTTPException(404, "Call not found.")
    return call

@app.post("/api/calls/{call_id}/ask")
def ask(call_id: str, body: Ask):
    call = store.get_call(call_id)
    if not call:
        raise HTTPException(404, "Call not found.")
    store.log_event(body.user_id, call_id, "ask")
    return llm.answer(body.question, call["transcript"], playbook.search(body.question))

@app.post("/api/calls/{call_id}/feedback")
def feedback(call_id: str, body: Feedback):
    if not store.get_call(call_id):
        raise HTTPException(404, "Call not found.")
    store.save_feedback(call_id, body.rating, body.confirmed, body.comment)
    return {"ok": True}

@app.post("/api/events")
def event(body: Event):
    store.log_event(body.user_id, body.call_id, body.name)
    return {"ok": True}

@app.get("/api/metrics")
def get_metrics(x_admin_token: str = Header("")):
    if ADMIN_TOKEN and x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Admin token required.")
    return metrics.compute()

@app.get("/")
def index():
    return FileResponse(BASE.parent / "frontend" / "index.html")

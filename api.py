import os
import uuid
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from agent import CustomerSupportAgent, SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Bookly Customer Support API", version="1.0.0")

_sessions: dict[str, CustomerSupportAgent] = {}

_STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


# ── Static ──────────────────────────────────────────────────────────────────

@app.get("/")
def serve_index():
    return FileResponse(os.path.join(_STATIC_DIR, "index.html"))


# ── Request / response models ───────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    tool_calls: list = []
    topic: str = "General Inquiry"
    instructions: str = ""
    usage: dict = {}


class SessionResponse(BaseModel):
    session_id: str


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.post("/sessions", response_model=SessionResponse, status_code=201)
def create_session():
    session_id = str(uuid.uuid4())
    _sessions[session_id] = CustomerSupportAgent()
    return {"session_id": session_id}


@app.get("/sessions")
def list_sessions():
    return {"sessions": list(_sessions.keys()), "count": len(_sessions)}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    agent = _sessions.get(req.session_id)
    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Create one first with POST /sessions.",
        )
    try:
        reply = agent.chat(req.message)
    except Exception as e:
        logging.exception("Error in agent.chat")
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "session_id": req.session_id,
        "response": reply,
        "tool_calls": agent.last_tool_calls,
        "topic": agent.last_topic,
        "instructions": agent.last_instructions,
        "usage": agent.last_usage,
    }


@app.post("/sessions/{session_id}/reset", response_model=SessionResponse)
def reset_session(session_id: str):
    agent = _sessions.get(session_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    agent.reset()
    return {"session_id": session_id}


@app.get("/system-prompt")
def get_system_prompt():
    return {"system_prompt": SYSTEM_PROMPT}


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    del _sessions[session_id]
    return {"message": "Session deleted."}

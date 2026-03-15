from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .model_client import generate_response
from .router import resolve_model

app = FastAPI(title="OpenBot API", version="0.1.0")

# Allow local frontend dev server to talk to the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "env": settings.ENV}


@app.get("/api/config")
def get_config():
    return {
        "env": settings.ENV,
        "models": [
            {"tag": "fast", "label": "GPT-4o-mini (fast)", "default_temperature": 0.6},
            {"tag": "creative", "label": "GPT-4o (creative)", "default_temperature": 0.9},
            {"tag": "logical", "label": "Claude-3-Opus (logical)", "default_temperature": 0.2},
        ],
    }


class ChatRequest(BaseModel):
    messages: list[dict]
    model_preference: str | None = "fast"
    temperature: float | None = None
    system_prompt: str | None = None


@app.post("/api/chat")
def chat(req: ChatRequest):
    model_config = resolve_model(req.model_preference or "fast")

    if req.temperature is not None:
        model_config["temperature"] = req.temperature

    if req.system_prompt:
        # Place system prompt at the start of the conversation
        system_msg = {"role": "system", "content": req.system_prompt}
        messages = [system_msg, *req.messages]
    else:
        messages = req.messages

    try:
        result = generate_response(messages, model_config)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

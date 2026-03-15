from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings

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


@app.post("/api/chat")
def chat(req: ChatRequest):
    # Stubbed response for early development.
    return {
        "model_preference": req.model_preference,
        "response": {
            "role": "assistant",
            "content": "This is a stubbed response. Replace with actual model logic.",
        },
        "trace": {
            "model_used": "stub",
            "duration_ms": 0,
        },
    }

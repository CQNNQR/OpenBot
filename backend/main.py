from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .model_client import generate_response, summarize_messages
from .router import resolve_model
from .storage import clear_messages, get_last_messages, init_db, save_message

app = FastAPI(title="OpenBot API", version="0.1.0")


@app.on_event("startup")
def startup():
    init_db()

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
    minimax: bool | None = False


@app.post("/api/chat")
def chat(req: ChatRequest):
    model_config = resolve_model(req.model_preference or "fast")

    if req.temperature is not None:
        model_config["temperature"] = req.temperature

    # Persist user message
    if req.messages:
        last_user = req.messages[-1]
        if last_user.get("role") == "user":
            save_message("user", last_user.get("content", ""))

    # Build context with summary if needed
    history = get_last_messages(20)
    context_summary = None
    if len(history) > 10:
        context_summary = summarize_messages(history, model_config)

    messages = req.messages or []
    if context_summary:
        messages = [
            {"role": "system", "content": f"Conversation summary: {context_summary}"},
            *messages,
        ]

    if req.system_prompt:
        messages = [{"role": "system", "content": req.system_prompt}, *messages]

    try:
        if req.minimax:
            minimax_model_config = resolve_minimax_model(req.model_preference or "fast")
            primary = generate_response(messages, model_config)
            secondary = generate_response(messages, minimax_model_config)

            # Persist both assistant responses
            if primary.get("response") and primary["response"].get("role") == "assistant":
                save_message("assistant", primary["response"].get("content", ""))
            if secondary.get("response") and secondary["response"].get("role") == "assistant":
                save_message("assistant", secondary["response"].get("content", ""))

            return {
                "minimax": True,
                "responses": [
                    {"label": "primary", **primary},
                    {"label": "secondary", **secondary},
                ],
                "trace": {
                    "context_summary": context_summary,
                    "primary": primary.get("trace"),
                    "secondary": secondary.get("trace"),
                },
            }
        result = generate_response(messages, model_config)

        # Persist assistant response
        if result.get("response") and result["response"].get("role") == "assistant":
            save_message("assistant", result["response"].get("content", ""))

        # Include context summary in trace for debugging
        if context_summary:
            result["trace"]["context_summary"] = context_summary

        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

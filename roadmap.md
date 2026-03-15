# Aura Roadmap

## Project Vision
**Aura** is a modular, UI-driven AI orchestration system built for speed, flexibility, and "vibe coding". The goal is to provide a transparent, component-based alternative to heavy frameworks like LangChain and OpenClaw.

### Core Principles
- **Modular over Monolithic**: Build swappable components, not one giant bot.
- **UI-First Logic**: If you can’t see or toggle it in the UI, it doesn’t exist.
- **Pure Python/JS**: Keep logic explicit with loops and conditionals; avoid hidden abstractions.
- **Traceability**: Every decision should be visible, logged, and debuggable.

---

## Getting Started (MVP Setup)
### Recommended Local Setup
1. Clone the repo.
2. Create a Python virtual environment (`python -m venv .venv`).
3. Install backend dependencies (`pip install -r backend/requirements.txt`).
4. Install frontend dependencies (`cd frontend && npm install`).
5. Copy `.env.example` to `.env` and fill in required variables.
6. Run backend (`uvicorn backend.main:app --reload --port 8000`) and frontend (`npm run dev`).

> Note: The backend uses `pydantic-settings` for configuration. If you see an import error related to `BaseSettings`, make sure `pip install -r backend/requirements.txt` is up to date.

---

## Project Structure (Expected)
```
/ (root)
  /backend
    main.py
    router.py
    memory.py
    model_map.py
    config.py
  /frontend
    src/
      components/
      pages/
      stores/
    public/
  /tools
    (auto-detected scripts)
  /data
    sqlite.db
  roadmap.md
  README.md
  copilot-instructions.md
```

> Recommendation: Keep conventions rigid. The backend should not import frontend code and vice versa.

---

## Configuration (Env & Settings)
We treat most runtime decisions as configuration to keep code simple.

### Environment Variables
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `LITELLM_API_KEY` (if used)
- `DATABASE_URL` (SQLite file or Supabase connection string)
- `AURA_MODELS_JSON` (optional path to a JSON model map)

### UI-Driven Config
- A JSON schema describing available model presets, tool toggles, and default temperatures.
- Stored in the backend and exposed to the frontend via a `/config` endpoint.

> Recommendation: Keep a single source of truth for config (e.g., `backend/config.py`).

---

## Data & Flow Overview
### Request Flow (High Level)
1. UI sends a request to `/api/chat` with:
   - `messages[]`
   - `model_preference` (e.g., `creative`, `logical`, `fast`)
   - `personaId` (optional)
   - tool toggles (e.g., `enable_search`, `enable_files`)
2. Backend uses **Router** to map `model_preference` → model spec.
3. Backend applies **Context Window Manager** (summarize prior messages into `Current State`).
4. Backend calls LiteLLM/OpenAI/Anthropic.
5. Response is saved to memory and returned with trace metadata.

### Trace & Logging
- Each request should return a `trace` object containing:
  - `model_used`
  - `call_duration`
  - `tool_calls` (if MCP tools were invoked)
  - `prompt_used`

> This enables the frontend "Thought Trace" panel.

---

## Key Systems
### Router Pattern (The Brain)
- Core idea: Let UI choose **intent**, not concrete model names.
- Router maps intent tags to model configs.
- Router should be simple, readable, and extensible.

**Example:**
```py
MODEL_MAP = {
  "creative": {"provider": "openai", "model": "gpt-4o", "temperature": 0.9},
  "logical": {"provider": "anthropic", "model": "claude-3-opus", "temperature": 0.2},
  "fast": {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.6},
}
```

> Recommendation: Keep router logic in `backend/router.py` and make it configurable via JSON.

### Context Window Manager (The Registry)
- Goal: avoid sending full history while preserving state.
- Approach:
  1. Store full history in DB.
  2. On each new request, retrieve last N messages.
  3. Call a summarization model (or use a local algorithm) to generate a compact "Current State".
  4. Prepend the summary to the prompt.

> Recommendation: Keep summarization optional; allow disabling for debugging.

### Tool Discovery & MCP (The Claws)
- Any file dropped into `/tools` should be:
  1. Discovered at runtime.
  2. Read for metadata (name, description, args).
  3. Exposed to the LLM as an available tool.

Example tool metadata format (YAML/JSON header in script):
```yaml
name: google_search
description: Search Google and return the top result.
args:
  - query: string
```

> Recommendation: Keep tool registration simple (inspect file headers or use a decorator).

---

## Phase-by-Phase Execution Plan (Revised)

### Phase 0: MVP Scope & Priors (Pre-work)
**Objective:** Get a minimal end-to-end pipeline working quickly.
- [x] Define the minimal data flow (frontend → backend → model → response).
- [x] Decide on initial model targets (OpenAI + one local or Anthropic).
- [x] Add skeleton folder structure and minimal `README.md` / `roadmap.md`.
- [ ] Create GitHub repo and push initial scaffold.

### Phase 1: The Visual Shell (The “Vibe” Setup)
**Objective:** Ship a UI that feels better than OpenClaw.
- [x] Build the dashboard yourself using React + Tailwind (no AI app-builder shortcuts).
- [x] Keep it “vibe coding” by iterating quickly in the UI and letting the design evolve.
- [x] Build UI components:
  - Sidebar for **Model Configuration** (temperature sliders, model toggles, intent tags).
  - Main **chat area** (message list + composer).
  - Real-time **Thought Trace** panel (logs RPCs, model calls, token usage).
- [x] Build a stubbed backend endpoint that returns canned responses.

### Phase 2: The Router & LiteLLM (The “Brain”)
**Objective:** Hook the UI to real models with minimal complexity.
- Add backend:
  - FastAPI server.
  - LiteLLM integration for OpenAI/Anthropic.
  - `router.py` for `model_preference` → model config mapping.
- Connect frontend to backend, send real user messages.
- Add basic auth/keys management.

### Phase 3: Infinite Memory & Context (The “Registry”)
**Objective:** Surpass LangChain memory management.
- Add a memory layer:
  - SQLite (or Supabase) storing message history & personas.
  - Context Window Manager to summarize last N messages.
- Add UI controls for memory:
  - “Reset conversation” button.
  - “View full history” toggle.

### Phase 4: Skills & MCP (The “Claws”)
**Objective:** Give Aura the ability to do things.
- Integrate MCP (Model Context Protocol) in backend.
- Implement tool discovery in `/tools`.
- Make tool usage visible in the Thought Trace.
- Add UI toggles to enable/disable tools per conversation.

---

## Success Metrics (How to beat the competition)
- **Latency**: The system should feel faster than LangChain (no abstraction bloat).
- **Control**: Ability to change the “Logic Model” mid-conversation via UI toggles.
- **Simplicity**: Backend code (e.g., `router.py`) should be readable by non-coders.
- **Traceability**: Every model call and tool use is visible in the UI.
- **Extensibility**: Adding a new tool or model should take < 15 minutes.

---

## Future Expansion: The “Meta-Agent”
- Build a self-optimizing agent.
- Prompt: “Watch my last 10 interactions. Suggest a new system prompt that would have made the AI’s answers more concise.”
- Add an evaluation loop: track which system prompts yield the highest user satisfaction.

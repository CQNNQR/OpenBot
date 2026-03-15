# Aura — Custom AI Orchestration System

Aura is a UI-driven, modular AI orchestration system built to be a flexible alternative to LangChain and OpenClaw. It focuses on transparency, performance, and "vibe coding" speed.

## 🚀 What Makes Aura Different?
- **Modular Components**: Swap models, memory stores, and tools without rewriting the whole bot.
- **UI-First Logic**: If you can’t toggle it in the UI, it doesn’t exist.
- **Pure Python & JS**: No hidden abstractions or opaque chains—everything is explicit.

## 🧱 Architecture Overview
- **Frontend**: React + Tailwind (via Bolt.new) control center.
- **Backend**: FastAPI + LiteLLM with a router-based model selection layer.
- **Memory**: SQLite or Supabase for chat history, personas, and context summaries.
- **Tools**: MCP for connecting the LLM to external capabilities like searches, file access, and terminal actions.

## 🛠️ Getting Started (Draft)

### Backend (FastAPI)
1. Create a Python venv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate    # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the backend server:
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

### Frontend (React + Vite)
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Run the dev server:
   ```bash
   npm run dev
   ```

### Notes
- Frontend is configured to proxy `/api` to `http://localhost:8000`.
- Copy `.env.example` to `.env` and set API keys (OpenAI, Anthropic) and other settings as needed.
- To push to GitHub, create a repo at https://github.com/CQNNQR/OpenBot and run:
  ```bash
  git remote add origin https://github.com/CQNNQR/OpenBot.git
  git push -u origin main
  ```

> Note: This repo is a work-in-progress. Follow `roadmap.md` for current priorities.

## 📌 Roadmap
See `roadmap.md` for detailed phase plans, feature goals, and success metrics.

## 🤝 Contributing
- Follow the **Vibe Coding Workflow** in `roadmap.md`.
- If you add a feature, **update `roadmap.md`** with what’s done and what’s next.

---

## 📣 Want to Help?
- Add new tools into `/tools` for automatic MCP discovery.
- Improve the router logic to map model preferences to more nuanced strategies.
- Build the Meta-Agent feature to self-optimize system prompts.

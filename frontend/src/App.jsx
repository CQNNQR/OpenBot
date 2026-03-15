import { useEffect, useMemo, useRef, useState } from "react";

function MessageBubble({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`bubble ${isUser ? "bubble-user" : "bubble-assistant"}`}>
      <div className="role">{isUser ? "You" : "OpenBot"}</div>
      <div className="text">{text}</div>
    </div>
  );
}

function Spinner({ size = 18 }) {
  return (
    <div className="spinner" style={{ width: size, height: size }}>
      <div />
      <div />
      <div />
      <div />
    </div>
  );
}

export default function App() {
  const [config, setConfig] = useState(null);
  const [status, setStatus] = useState("Loading...");
  const [modelPreference, setModelPreference] = useState("fast");
  const [primaryAgent, setPrimaryAgent] = useState("openai");
  const [temperature, setTemperature] = useState(0.6);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [minimax, setMinimax] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState([]);
  const [trace, setTrace] = useState(null);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState(null);
  const messagesRef = useRef(null);

  const modelOptions = useMemo(() => config?.models ?? [], [config]);
  const activeModel = useMemo(
    () => modelOptions.find((m) => m.tag === modelPreference) ?? modelOptions[0],
    [modelOptions, modelPreference]
  );

  useEffect(() => {
    if (activeModel?.default_temperature) {
      setTemperature(activeModel.default_temperature);
    }
  }, [activeModel]);

  useEffect(() => {
    fetch("/api/config")
      .then((res) => res.json())
      .then((json) => {
        setConfig(json);
        setStatus("Ready");
        if (json.agents?.length) {
          setPrimaryAgent(json.agents[0].tag);
        }
      })
      .catch((err) => {
        console.error(err);
        setStatus("Failed to load config");
        setError("Unable to load config.");
      });
  }, []);

  useEffect(() => {
    if (!messagesRef.current) return;
    messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
  }, [messages]);

  const appendMessage = (msg) => setMessages((prev) => [...prev, msg]);

  const sendMessage = async () => {
    if (!draft.trim() || isSending) return;

    setError(null);
    setIsSending(true);

    const outgoing = { role: "user", content: draft.trim() };
    appendMessage(outgoing);
    setDraft("");

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, outgoing],
          model_preference: modelPreference,
          primary_agent: primaryAgent,
          temperature,
          system_prompt: systemPrompt || undefined,
          minimax,
        }),
      });

      if (!resp.ok) {
        const payload = await resp.json().catch(() => null);
        throw new Error(payload?.detail ?? "Request failed");
      }

      const data = await resp.json();
      if (data.minimax && Array.isArray(data.responses)) {
        data.responses.forEach((resp) => {
          if (resp.response) {
            appendMessage({
              role: "assistant",
              content: `[${resp.label}] ${resp.response.content}`,
            });
          }
        });
        setTrace(data.trace ?? null);
      } else if (data.response) {
        appendMessage(data.response);
        setTrace(data.trace ?? null);
      }
    } catch (err) {
      console.error(err);
      setError(String(err));
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      sendMessage();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setTrace(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>OpenBot</h1>
          <div className="sub">Vibe coding a modular AI orchestration system.</div>
        </div>

        <div className="header-meta">
          <div className="label">Agent</div>
          <select
            value={primaryAgent}
            onChange={(e) => setPrimaryAgent(e.target.value)}
          >
            {config?.agents?.map((a) => (
              <option key={a.tag} value={a.tag}>
                {a.label}
              </option>
            ))}
          </select>

          <div className="label">Mode</div>
          <select
            value={modelPreference}
            onChange={(e) => setModelPreference(e.target.value)}
          >
            {modelOptions.map((m) => (
              <option key={m.tag} value={m.tag}>
                {m.label}
              </option>
            ))}
          </select>

          <div className="model-tag">{activeModel?.model ?? "loading..."}</div>
        </div>
      </header>

      <main className="main">
        <section className="panel chat-panel">
          <div className="panel-header">
            <h2>Chat</h2>
            <div className="panel-actions">
              <button className="ghost" onClick={clearConversation}>
                Clear
              </button>
              <div className="status-pill">
                {isSending ? (
                  <span>
                    <Spinner size={14} /> Sending...
                  </span>
                ) : (
                  status
                )}
              </div>
            </div>
          </div>

          <div className="chat">
            <div className="messages" ref={messagesRef}>
              {messages.length === 0 && (
                <p className="empty">Ask something to start the conversation.</p>
              )}
              {messages.map((msg, idx) => (
                <MessageBubble key={idx} role={msg.role} text={msg.content} />
              ))}
            </div>

            <div className="composer">
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type a message... (Ctrl+Enter to send)"
                rows={3}
              />
              <div className="composer-actions">
                <div className="send-hint">
                  <span className="hint-label">Send:</span> Ctrl+Enter
                </div>
                <button
                  onClick={sendMessage}
                  className="primary"
                  disabled={isSending || !draft.trim()}
                >
                  {isSending ? "Sending…" : "Send"}
                </button>
              </div>
              {error && <div className="error">{error}</div>}
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Trace</h2>
          </div>
          <pre className="trace-block">
            {trace ? JSON.stringify(trace, null, 2) : "No trace yet."}
          </pre>
        </section>

        <section className="panel">
          <div className="panel-header">
            <h2>Quick Config</h2>
          </div>
          <div className="config">
            <label>
              <span>Model preference</span>
              <select
                value={modelPreference}
                onChange={(e) => setModelPreference(e.target.value)}
              >
                {modelOptions.map((m) => (
                  <option key={m.tag} value={m.tag}>
                    {m.label}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Temperature</span>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
              />
              <div className="temp-label">{temperature.toFixed(2)}</div>
            </label>

            <label className="checkbox">
              <input
                type="checkbox"
                checked={minimax}
                onChange={(e) => setMinimax(e.target.checked)}
              />
              <span>Minimax (dual-call)</span>
            </label>

            <label>
              <span>System prompt</span>
              <input
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                placeholder="Optional system prompt (e.g. ‘You are a friendly assistant.’)"
              />
            </label>

            <label>
              <span>Current model</span>
              <input value={activeModel?.model ?? "..."} readOnly />
            </label>

            <p className="note">
              Toggle the model used for each request and tweak temperature in real time.
              The backend router maps the preference to a concrete model.
            </p>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div>OpenBot • v0.1</div>
      </footer>
    </div>
  );
}

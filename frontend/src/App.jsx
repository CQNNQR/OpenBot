import { useEffect, useMemo, useState } from "react";

function MessageBubble({ role, text }) {
  const isUser = role === "user";
  return (
    <div className={`bubble ${isUser ? "bubble-user" : "bubble-assistant"}`}>
      <div className="role">{isUser ? "You" : "OpenBot"}</div>
      <div className="text">{text}</div>
    </div>
  );
}

export default function App() {
  const [config, setConfig] = useState(null);
  const [status, setStatus] = useState("Loading...");
  const [modelPreference, setModelPreference] = useState("fast");
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState([]);
  const [trace, setTrace] = useState(null);

  const modelOptions = useMemo(() => config?.models ?? [], [config]);

  useEffect(() => {
    fetch("/api/config")
      .then((res) => res.json())
      .then((json) => {
        setConfig(json);
        setStatus("Ready");
      })
      .catch((err) => {
        console.error(err);
        setStatus("Failed to load config");
      });
  }, []);

  const sendMessage = async () => {
    if (!draft.trim()) return;

    const outgoing = { role: "user", content: draft.trim() };
    setMessages((prev) => [...prev, outgoing]);
    setDraft("");

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [...messages, outgoing],
          model_preference: modelPreference,
        }),
      });

      const data = await resp.json();
      if (data.response) {
        setMessages((prev) => [...prev, data.response]);
        setTrace(data.trace ?? null);
      }
    } catch (err) {
      console.error(err);
      setStatus("Error sending message");
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>OpenBot</h1>
        <div className="sub">Vibe coding a modular AI orchestration system.</div>
      </header>

      <main className="main">
        <section className="panel">
          <h2>Chat</h2>
          <div className="chat">
            <div className="messages">
              {messages.length === 0 && <p className="empty">Send a message to start the conversation.</p>}
              {messages.map((msg, idx) => (
                <MessageBubble key={idx} role={msg.role} text={msg.content} />
              ))}
            </div>
            <div className="composer">
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                placeholder="Type a message..."
                rows={3}
              />
              <div className="composer-actions">
                <select value={modelPreference} onChange={(e) => setModelPreference(e.target.value)}>
                  {modelOptions.map((m) => (
                    <option key={m.tag} value={m.tag}>
                      {m.label}
                    </option>
                  ))}
                </select>
                <button onClick={sendMessage} className="primary">
                  Send
                </button>
              </div>
            </div>
          </div>
        </section>

        <section className="panel">
          <h2>Trace</h2>
          <pre>{trace ? JSON.stringify(trace, null, 2) : "No trace yet."}</pre>
        </section>

        <section className="panel">
          <h2>Status</h2>
          <p>{status}</p>
        </section>
      </main>

      <footer className="footer">
        <div>OpenBot • v0.1</div>
      </footer>
    </div>
  );
}

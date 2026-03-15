import { useEffect, useState } from "react";

export default function App() {
  const [config, setConfig] = useState(null);
  const [status, setStatus] = useState("Loading...");

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

  return (
    <div className="app">
      <header className="header">
        <h1>OpenBot</h1>
        <div className="sub">Vibe coding a modular AI orchestration system.</div>
      </header>

      <main className="main">
        <section className="panel">
          <h2>Status</h2>
          <p>{status}</p>
        </section>

        <section className="panel">
          <h2>Models</h2>
          {config ? (
            <ul>
              {config.models.map((m) => (
                <li key={m.tag}>
                  <strong>{m.label}</strong> ({m.tag})
                </li>
              ))}
            </ul>
          ) : (
            <p>Loading…</p>
          )}
        </section>
      </main>

      <footer className="footer">
        <div>OpenBot • v0.1</div>
      </footer>
    </div>
  );
}

import { useEffect, useState } from "react";
import { getHealth, type Health } from "./api/client";

export function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((e: unknown) => setError(String(e)));
  }, []);

  return (
    <main className="app-shell">
      <header>
        <h1>Weather Tracking &amp; Analysis Dashboard</h1>
        <p className="subtitle">
          Ingest, analyse and visualise weather time-series data.
        </p>
      </header>
      <section className="status-card">
        <h2>Backend status</h2>
        {error && <p className="status status--error">Unreachable: {error}</p>}
        {!error && !health && <p className="status">Checking…</p>}
        {health && (
          <p className="status status--ok">
            {health.status} · {health.app} ({health.environment})
          </p>
        )}
      </section>
    </main>
  );
}

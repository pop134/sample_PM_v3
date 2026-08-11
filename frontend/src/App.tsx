import { useEffect, useState } from "react";
import { AppLayout } from "./components/AppLayout";
import { Card } from "./components/Card";
import { DashboardGrid } from "./components/DashboardGrid";
import { StatTile } from "./components/StatTile";
import { getHealth, type Health } from "./api/client";

export function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch((e: unknown) => setError(String(e)));
  }, []);

  return (
    <AppLayout>
      <DashboardGrid>
        <Card title="Overview">
          <p className="muted">
            Ingest, analyse and visualise weather time-series data. Widgets wire up
            to the API in the following tasks.
          </p>
        </Card>
        <Card title="Backend status">
          {error && <StatTile label="API" value="Unreachable" hint={error} />}
          {!error && !health && <StatTile label="API" value="Checking…" />}
          {health && (
            <StatTile label="API" value={health.status} hint={`${health.app} · ${health.environment}`} />
          )}
        </Card>
      </DashboardGrid>
    </AppLayout>
  );
}

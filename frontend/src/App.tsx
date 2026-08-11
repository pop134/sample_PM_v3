import { useEffect, useState } from "react";
import { AppLayout } from "./components/AppLayout";
import { Card } from "./components/Card";
import { DashboardGrid } from "./components/DashboardGrid";
import { Nav } from "./components/Nav";
import { StatTile } from "./components/StatTile";
import { DEFAULT_VIEW, type ViewId } from "./navigation/views";
import { getHealth, type Health } from "./api/client";

export function App() {
  const [view, setView] = useState<ViewId>(DEFAULT_VIEW);
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth().then(setHealth).catch((e: unknown) => setError(String(e)));
  }, []);

  return (
    <AppLayout nav={<Nav active={view} onSelect={setView} />}>
      {view === "dashboard" && (
        <DashboardGrid>
          <Card title="Overview">
            <p className="muted">Current conditions and trends for your locations.</p>
          </Card>
          <Card title="Backend status">
            {error && <StatTile label="API" value="Unreachable" hint={error} />}
            {!error && !health && <StatTile label="API" value="Checking…" />}
            {health && (
              <StatTile label="API" value={health.status} hint={`${health.app} · ${health.environment}`} />
            )}
          </Card>
        </DashboardGrid>
      )}
      {view === "analytics" && <Card title="Analytics"><p className="muted">Trend charts arrive in task 1.4.4.</p></Card>}
      {view === "alerts" && <Card title="Alerts"><p className="muted">Alert feed arrives with the alerts UI.</p></Card>}
      {view === "settings" && <Card title="Settings"><p className="muted">Preferences arrive in task 1.6.2.</p></Card>}
    </AppLayout>
  );
}

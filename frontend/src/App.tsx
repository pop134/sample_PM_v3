import { useState } from "react";
import { AppLayout } from "./components/AppLayout";
import { Card } from "./components/Card";
import { DashboardGrid } from "./components/DashboardGrid";
import { Nav } from "./components/Nav";
import { Spinner } from "./components/Spinner";
import { CurrentConditions } from "./features/weather/CurrentConditions";
import { TrendChart } from "./features/charts/TrendChart";
import { DEFAULT_LOCATION, useCurrentConditions } from "./features/weather/useCurrentConditions";
import { DEFAULT_VIEW, type ViewId } from "./navigation/views";

function DashboardView() {
  const { data, loading, error, notFound } = useCurrentConditions(
    DEFAULT_LOCATION.lat, DEFAULT_LOCATION.lon,
  );
  return (
    <DashboardGrid>
      {loading && <Card title="Current"><Spinner /></Card>}
      {error && <Card title="Current"><p className="muted">Couldn’t load conditions: {error}</p></Card>}
      {notFound && <Card title="Current"><p className="muted">No data yet for {DEFAULT_LOCATION.name}.</p></Card>}
      {data && <CurrentConditions observation={data} />}
      <Card title="Overview">
        <p className="muted">Trends, alerts and multiple locations arrive in later tasks.</p>
      </Card>
    </DashboardGrid>
  );
}

export function App() {
  const [view, setView] = useState<ViewId>(DEFAULT_VIEW);
  return (
    <AppLayout nav={<Nav active={view} onSelect={setView} />}>
      {view === "dashboard" && <DashboardView />}
      {view === "analytics" && <TrendChart lat={DEFAULT_LOCATION.lat} lon={DEFAULT_LOCATION.lon} />}
      {view === "alerts" && <Card title="Alerts"><p className="muted">Alert feed arrives with the alerts UI.</p></Card>}
      {view === "settings" && <Card title="Settings"><p className="muted">Preferences arrive in task 1.6.2.</p></Card>}
    </AppLayout>
  );
}

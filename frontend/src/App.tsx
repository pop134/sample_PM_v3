import { useState } from "react";
import { AppLayout } from "./components/AppLayout";
import { Card } from "./components/Card";
import { DashboardGrid } from "./components/DashboardGrid";
import { Nav } from "./components/Nav";
import { Spinner } from "./components/Spinner";
import { TrendChart } from "./features/charts/TrendChart";
import { LocationBar } from "./features/locations/LocationBar";
import { useLocations } from "./features/locations/LocationContext";
import { CurrentConditions } from "./features/weather/CurrentConditions";
import { useCurrentConditions } from "./features/weather/useCurrentConditions";
import { DEFAULT_VIEW, type ViewId } from "./navigation/views";

function DashboardView() {
  const { active } = useLocations();
  const { data, loading, error, notFound } = useCurrentConditions(active.latitude, active.longitude);
  return (
    <DashboardGrid>
      {loading && <Card title="Current"><Spinner /></Card>}
      {error && <Card title="Current"><p className="muted">Couldn’t load conditions: {error}</p></Card>}
      {notFound && <Card title="Current"><p className="muted">No data yet for {active.name}.</p></Card>}
      {data && <CurrentConditions observation={data} />}
      <Card title="Overview">
        <p className="muted">Switch or add locations above; trends live under Analytics.</p>
      </Card>
    </DashboardGrid>
  );
}

function AnalyticsView() {
  const { active } = useLocations();
  return <TrendChart lat={active.latitude} lon={active.longitude} />;
}

export function App() {
  const [view, setView] = useState<ViewId>(DEFAULT_VIEW);
  return (
    <AppLayout nav={<><LocationBar /><Nav active={view} onSelect={setView} /></>}>
      {view === "dashboard" && <DashboardView />}
      {view === "analytics" && <AnalyticsView />}
      {view === "alerts" && <Card title="Alerts"><p className="muted">Alert feed arrives with the alerts UI.</p></Card>}
      {view === "settings" && <Card title="Settings"><p className="muted">Preferences arrive in task 1.6.2.</p></Card>}
    </AppLayout>
  );
}

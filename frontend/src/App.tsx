import { useState } from "react";
import { AppLayout } from "./components/AppLayout";
import { Card } from "./components/Card";
import { DashboardGrid } from "./components/DashboardGrid";
import { Nav } from "./components/Nav";
import { EmptyState } from "./components/states/EmptyState";
import { ErrorState } from "./components/states/ErrorState";
import { Skeleton } from "./components/states/Skeleton";
import { viewStatus } from "./components/states/status";
import { TrendChart } from "./features/charts/TrendChart";
import { LocationBar } from "./features/locations/LocationBar";
import { useLocations } from "./features/locations/LocationContext";
import { AutoRefreshControl } from "./features/realtime/AutoRefreshControl";
import { DEFAULT_REFRESH_MS, labelForMs } from "./features/realtime/refresh";
import { CurrentConditions } from "./features/weather/CurrentConditions";
import { useCurrentConditions } from "./features/weather/useCurrentConditions";
import { useInterval } from "./lib/useInterval";
import { DEFAULT_VIEW, type ViewId } from "./navigation/views";

function DashboardView() {
  const { active } = useLocations();
  const query = useCurrentConditions(active.latitude, active.longitude);
  const status = viewStatus(query);
  const [intervalMs, setIntervalMs] = useState<number | null>(DEFAULT_REFRESH_MS);

  useInterval(() => query.refetch(), intervalMs);

  return (
    <DashboardGrid>
      {status === "ready" && query.data ? (
        <CurrentConditions observation={query.data} />
      ) : (
        <Card title="Current conditions">
          {status === "loading" && <Skeleton />}
          {status === "error" && <ErrorState message={query.error ?? "Failed to load"} onRetry={query.refetch} />}
          {status === "empty" && <EmptyState message={`No data yet for ${active.name}.`} icon="🌤️" />}
        </Card>
      )}
      <Card title="Overview">
        <p className="muted">
          {intervalMs === null
            ? "Live updates are off."
            : `Refreshing every ${labelForMs(intervalMs)} without a page reload.`}
        </p>
        <AutoRefreshControl value={intervalMs} onChange={setIntervalMs} />
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

import { Card } from "../../components/Card";
import { StatTile } from "../../components/StatTile";
import { formatDateTime } from "../../lib/format";
import type { Observation } from "../../api/types";
import { buildSummaryTiles, type TempUnit } from "./summary";

interface CurrentConditionsProps {
  observation: Observation;
  unit?: TempUnit;
}

export function CurrentConditions({ observation, unit = "c" }: CurrentConditionsProps) {
  const tiles = buildSummaryTiles(observation, unit);
  const name = observation.location_name ?? `${observation.latitude}, ${observation.longitude}`;
  return (
    <Card title={`Current — ${name}`} className="current">
      {observation.condition && <p className="current__condition">{observation.condition}</p>}
      <div className="current__tiles">
        {tiles.map((t) => (
          <StatTile key={t.label} label={t.label} value={t.value} />
        ))}
      </div>
      <p className="muted current__ts">Observed {formatDateTime(observation.observed_at)}</p>
    </Card>
  );
}

// Build the summary tiles for the current-conditions widget (WBS 1.4.3). Pure.
import { formatPercent, formatTemp, formatWind } from "../../lib/format";
import type { Observation } from "../../api/types";

export interface SummaryTile {
  label: string;
  value: string;
}

export type TempUnit = "c" | "f";

export function buildSummaryTiles(obs: Observation, unit: TempUnit = "c"): SummaryTile[] {
  return [
    { label: "Temperature", value: formatTemp(obs.temperature_c, unit) },
    { label: "Feels like", value: formatTemp(obs.feels_like_c, unit) },
    { label: "Humidity", value: formatPercent(obs.humidity_pct) },
    { label: "Wind", value: formatWind(obs.wind_speed_ms) },
  ];
}

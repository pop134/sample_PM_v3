// Selected-locations persistence helpers (WBS 1.4.5). Pure/tested.
import type { LocationSummary } from "../../api/types";

export const LOCATIONS_STORAGE_KEY = "weather-dashboard-locations";

// Seed so the dashboard has something before the user searches.
export const DEFAULT_LOCATIONS: LocationSummary[] = [
  { id: -1, name: "London", latitude: 51.5074, longitude: -0.1278 },
];

export function serializeLocations(locations: LocationSummary[]): string {
  return JSON.stringify(locations);
}

export function parseLocations(raw: string | null): LocationSummary[] {
  if (!raw) return DEFAULT_LOCATIONS;
  try {
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return DEFAULT_LOCATIONS;
    const valid = parsed.filter(
      (l): l is LocationSummary =>
        typeof l === "object" && l !== null &&
        typeof (l as LocationSummary).id === "number" &&
        typeof (l as LocationSummary).name === "string",
    );
    return valid.length > 0 ? valid : DEFAULT_LOCATIONS;
  } catch {
    return DEFAULT_LOCATIONS;
  }
}

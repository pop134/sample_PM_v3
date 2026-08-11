// Location search helpers (WBS 1.4.5). Pure/tested.
import type { LocationSummary } from "../../api/types";

/** Case-insensitive substring match on name; empty query returns all. */
export function filterLocations(
  locations: LocationSummary[], query: string,
): LocationSummary[] {
  const q = query.trim().toLowerCase();
  if (!q) return locations;
  return locations.filter((l) => l.name.toLowerCase().includes(q));
}

/** Add a location, de-duplicated by id. Returns a new array. */
export function addLocation(
  selected: LocationSummary[], location: LocationSummary,
): LocationSummary[] {
  if (selected.some((l) => l.id === location.id)) return selected;
  return [...selected, location];
}

export function removeLocation(
  selected: LocationSummary[], id: number,
): LocationSummary[] {
  return selected.filter((l) => l.id !== id);
}

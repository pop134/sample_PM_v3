import { describe, expect, it } from "vitest";
import type { LocationSummary } from "../../api/types";
import { addLocation, filterLocations, removeLocation } from "./search";

const locs: LocationSummary[] = [
  { id: 1, name: "London", latitude: 51.5, longitude: -0.12 },
  { id: 2, name: "Paris", latitude: 48.85, longitude: 2.35 },
  { id: 3, name: "Portland", latitude: 45.52, longitude: -122.68 },
];

describe("location search", () => {
  it("filters case-insensitively", () => {
    expect(filterLocations(locs, "p").map((l) => l.name)).toEqual(["Paris", "Portland"]);
    expect(filterLocations(locs, "LON").map((l) => l.name)).toEqual(["London"]);
    expect(filterLocations(locs, "")).toHaveLength(3);
  });

  it("adds without duplicates and removes", () => {
    let sel = addLocation([], locs[0]);
    sel = addLocation(sel, locs[0]);
    expect(sel).toHaveLength(1);
    sel = addLocation(sel, locs[1]);
    expect(sel.map((l) => l.id)).toEqual([1, 2]);
    expect(removeLocation(sel, 1).map((l) => l.id)).toEqual([2]);
  });
});

import { describe, expect, it } from "vitest";
import { DEFAULT_LOCATIONS, parseLocations, serializeLocations } from "./state";

describe("location persistence", () => {
  it("round-trips locations", () => {
    const locs = [{ id: 5, name: "Berlin", latitude: 52.52, longitude: 13.4 }];
    expect(parseLocations(serializeLocations(locs))).toEqual(locs);
  });

  it("falls back to defaults on null/garbage", () => {
    expect(parseLocations(null)).toEqual(DEFAULT_LOCATIONS);
    expect(parseLocations("not json")).toEqual(DEFAULT_LOCATIONS);
    expect(parseLocations("[]")).toEqual(DEFAULT_LOCATIONS);
    expect(parseLocations('[{"bad":1}]')).toEqual(DEFAULT_LOCATIONS);
  });
});

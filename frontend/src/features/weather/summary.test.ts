import { describe, expect, it } from "vitest";
import type { Observation } from "../../api/types";
import { buildSummaryTiles } from "./summary";

const obs: Observation = {
  id: 1, location_name: "London", latitude: 51.5, longitude: -0.12,
  observed_at: "2026-08-01T18:00:00Z", temperature_c: 18.4, feels_like_c: 17.9,
  humidity_pct: 72, pressure_hpa: 1012, wind_speed_ms: 4.15, wind_deg: 210,
  condition: "light rain", provider: "openweather",
};

describe("buildSummaryTiles", () => {
  it("builds four labelled tiles in celsius", () => {
    const tiles = buildSummaryTiles(obs);
    expect(tiles.map((t) => t.label)).toEqual(["Temperature", "Feels like", "Humidity", "Wind"]);
    expect(tiles[0].value).toBe("18.4°C");
    expect(tiles[2].value).toBe("72%");
    expect(tiles[3].value).toBe("4.2 m/s");
  });

  it("supports fahrenheit", () => {
    expect(buildSummaryTiles(obs, "f")[0].value).toBe("65.1°F");
  });
});

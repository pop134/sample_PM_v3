import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Observation } from "../../api/types";
import { CurrentConditions } from "./CurrentConditions";

const obs: Observation = {
  id: 1, location_name: "London", latitude: 51.5, longitude: -0.12,
  observed_at: "2026-08-01T18:00:00Z", temperature_c: 18.4, feels_like_c: 17.9,
  humidity_pct: 72, pressure_hpa: 1012, wind_speed_ms: 4.1, wind_deg: 210,
  condition: "light rain", provider: "openweather",
};

describe("CurrentConditions", () => {
  it("renders location, condition and temperature tile", () => {
    render(<CurrentConditions observation={obs} />);
    expect(screen.getByText(/Current — London/)).toBeTruthy();
    expect(screen.getByText("light rain")).toBeTruthy();
    expect(screen.getByText("18.4°C")).toBeTruthy();
  });
});

import { describe, expect, it } from "vitest";
import { formatPercent, formatTemp, formatWind } from "./format";

describe("formatters", () => {
  it("formats celsius and fahrenheit", () => {
    expect(formatTemp(20)).toBe("20°C");
    expect(formatTemp(0, "f")).toBe("32°F");
    expect(formatTemp(null)).toBe("—");
  });

  it("formats percent and wind", () => {
    expect(formatPercent(72.4)).toBe("72%");
    expect(formatPercent(null)).toBe("—");
    expect(formatWind(4.15)).toBe("4.2 m/s");
    expect(formatWind(undefined)).toBe("—");
  });
});

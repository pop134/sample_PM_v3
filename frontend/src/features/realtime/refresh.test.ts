import { describe, expect, it } from "vitest";
import { formatAgo, REFRESH_INTERVALS, resolveDelay } from "./refresh";

describe("auto-refresh config", () => {
  it("offers Off + timed intervals", () => {
    expect(REFRESH_INTERVALS[0]).toEqual({ label: "Off", ms: null });
    expect(REFRESH_INTERVALS.some((o) => o.ms === 60_000)).toBe(true);
  });

  it("resolves the effective delay", () => {
    expect(resolveDelay(true, 30_000)).toBe(30_000);
    expect(resolveDelay(false, 30_000)).toBeNull();
    expect(resolveDelay(true, null)).toBeNull();
  });

  it("formats elapsed time", () => {
    expect(formatAgo(5_000)).toBe("5s ago");
    expect(formatAgo(90_000)).toBe("1m ago");
    expect(formatAgo(3_600_000)).toBe("1h ago");
  });
});

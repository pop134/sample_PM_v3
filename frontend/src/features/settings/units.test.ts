import { describe, expect, it } from "vitest";
import { isTempUnit, otherUnit, unitLabel } from "./units";

describe("unit helpers", () => {
  it("validates and toggles units", () => {
    expect(isTempUnit("c")).toBe(true);
    expect(isTempUnit("k")).toBe(false);
    expect(otherUnit("c")).toBe("f");
    expect(otherUnit("f")).toBe("c");
  });

  it("labels units", () => {
    expect(unitLabel("c")).toContain("Celsius");
    expect(unitLabel("f")).toContain("Fahrenheit");
  });
});

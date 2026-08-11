import { describe, expect, it } from "vitest";
import { buildLinePath, extent, scaleLinear } from "./scale";

describe("chart scale helpers", () => {
  it("computes extent and pads a flat series", () => {
    expect(extent([3, 1, 9, 4])).toEqual([1, 9]);
    expect(extent([])).toEqual([0, 1]);
    expect(extent([5, 5, 5])).toEqual([4, 6]);
  });

  it("maps domain to range linearly", () => {
    const s = scaleLinear([0, 10], [0, 100]);
    expect(s(0)).toBe(0);
    expect(s(5)).toBe(50);
    expect(s(10)).toBe(100);
  });

  it("builds an SVG path", () => {
    const path = buildLinePath([{ x: 0, y: 0 }, { x: 10, y: 20 }]);
    expect(path).toBe("M 0 0 L 10 20");
    expect(buildLinePath([])).toBe("");
  });
});

import { describe, expect, it } from "vitest";
import { breakpointFor, isMobile, isNavVisible } from "./responsive";

describe("responsive helpers", () => {
  it("classifies widths", () => {
    expect(breakpointFor(400)).toBe("mobile");
    expect(breakpointFor(800)).toBe("tablet");
    expect(breakpointFor(1440)).toBe("desktop");
  });

  it("flags mobile", () => {
    expect(isMobile(500)).toBe(true);
    expect(isMobile(900)).toBe(false);
  });
});

describe("isNavVisible", () => {
  it("always shows on desktop, toggles on mobile", () => {
    expect(isNavVisible(false, false)).toBe(true);
    expect(isNavVisible(true, false)).toBe(false);
    expect(isNavVisible(true, true)).toBe(true);
  });
});

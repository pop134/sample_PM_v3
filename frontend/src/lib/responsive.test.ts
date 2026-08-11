import { describe, expect, it } from "vitest";
import { breakpointFor, isMobile } from "./responsive";

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

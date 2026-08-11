import { describe, expect, it } from "vitest";
import { getInitialTheme, isTheme, nextTheme } from "./theme";

describe("theme helpers", () => {
  it("prefers a valid stored theme", () => {
    expect(getInitialTheme("dark", false)).toBe("dark");
    expect(getInitialTheme("light", true)).toBe("light");
  });

  it("falls back to OS preference then light", () => {
    expect(getInitialTheme(null, true)).toBe("dark");
    expect(getInitialTheme(null, false)).toBe("light");
    expect(getInitialTheme("garbage", false)).toBe("light");
  });

  it("toggles and validates", () => {
    expect(nextTheme("light")).toBe("dark");
    expect(nextTheme("dark")).toBe("light");
    expect(isTheme("dark")).toBe(true);
    expect(isTheme("x")).toBe(false);
  });
});

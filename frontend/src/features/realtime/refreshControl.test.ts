import { describe, expect, it } from "vitest";
import { labelForMs } from "./refresh";

describe("labelForMs", () => {
  it("maps ms to its interval label", () => {
    expect(labelForMs(null)).toBe("Off");
    expect(labelForMs(60_000)).toBe("1m");
    expect(labelForMs(12_345)).toBe("Custom");
  });
});

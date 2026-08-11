import { describe, expect, it } from "vitest";
import { DEFAULT_VIEW, isViewId, VIEWS } from "./views";

describe("views", () => {
  it("has the four dashboard sections", () => {
    expect(VIEWS.map((v) => v.id)).toEqual(["dashboard", "analytics", "alerts", "settings"]);
  });

  it("validates view ids", () => {
    expect(isViewId("alerts")).toBe(true);
    expect(isViewId("nope")).toBe(false);
    expect(isViewId(DEFAULT_VIEW)).toBe(true);
  });
});

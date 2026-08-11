import { describe, expect, it } from "vitest";
import { viewStatus } from "./status";

const base = { loading: false, error: null, notFound: false, data: null };

describe("viewStatus", () => {
  it("prioritises error, then empty(notFound)", () => {
    expect(viewStatus({ ...base, error: "boom" })).toBe("error");
    expect(viewStatus({ ...base, notFound: true })).toBe("empty");
  });

  it("is ready with data, loading when pending", () => {
    expect(viewStatus({ ...base, data: { x: 1 } })).toBe("ready");
    expect(viewStatus({ ...base, loading: true })).toBe("loading");
  });

  it("treats blank data as empty via isEmpty", () => {
    expect(viewStatus({ ...base, data: [] as number[] }, (d) => d.length === 0)).toBe("empty");
    expect(viewStatus({ ...base, data: [1] }, (d) => d.length === 0)).toBe("ready");
  });
});

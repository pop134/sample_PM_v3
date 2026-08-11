import { describe, expect, it } from "vitest";
import { buildQuery } from "./query";

describe("buildQuery", () => {
  it("builds a query string and skips empty params", () => {
    expect(buildQuery({ lat: 51.5, lon: -0.12, provider: undefined })).toBe("?lat=51.5&lon=-0.12");
    expect(buildQuery({ a: null, b: "", c: 0 })).toBe("?c=0");
    expect(buildQuery({})).toBe("");
  });

  it("encodes values", () => {
    expect(buildQuery({ q: "a b&c" })).toBe("?q=a%20b%26c");
  });
});

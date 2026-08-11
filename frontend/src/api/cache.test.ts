import { describe, expect, it } from "vitest";
import { QueryCache } from "./cache";

function clockOf(ref: { t: number }) {
  return () => ref.t;
}

describe("QueryCache", () => {
  it("stores and retrieves values", () => {
    const cache = new QueryCache(1000);
    cache.set("k", { n: 1 });
    expect(cache.get<{ n: number }>("k")?.value).toEqual({ n: 1 });
    expect(cache.get("missing")).toBeUndefined();
  });

  it("reports staleness against the TTL", () => {
    const ref = { t: 0 };
    const cache = new QueryCache(1000, clockOf(ref));
    expect(cache.isStale("k")).toBe(true); // absent
    cache.set("k", 1);
    expect(cache.isStale("k")).toBe(false);
    ref.t = 1000;
    expect(cache.isStale("k")).toBe(true); // aged out
  });

  it("invalidates one key or all", () => {
    const cache = new QueryCache(1000);
    cache.set("a", 1);
    cache.set("b", 2);
    cache.invalidate("a");
    expect(cache.get("a")).toBeUndefined();
    expect(cache.size).toBe(1);
    cache.invalidate();
    expect(cache.size).toBe(0);
  });
});

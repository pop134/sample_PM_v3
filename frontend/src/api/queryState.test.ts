import { describe, expect, it } from "vitest";
import { cachedState } from "./queryState";

describe("cachedState", () => {
  it("renders a cached value immediately", () => {
    expect(cachedState({ value: 42, storedAt: 0 })).toEqual({
      data: 42, loading: false, error: null, notFound: false,
    });
  });

  it("starts loading when nothing is cached", () => {
    expect(cachedState(undefined)).toEqual({
      data: null, loading: true, error: null, notFound: false,
    });
  });
});

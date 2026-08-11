import { describe, expect, it } from "vitest";
import { authHeader, loadToken } from "./session";

describe("auth session", () => {
  it("loads a non-empty token", () => {
    expect(loadToken("abc")).toBe("abc");
    expect(loadToken("")).toBeNull();
    expect(loadToken(null)).toBeNull();
  });

  it("builds an auth header", () => {
    expect(authHeader("t")).toEqual({ Authorization: "Bearer t" });
    expect(authHeader(null)).toEqual({});
  });
});

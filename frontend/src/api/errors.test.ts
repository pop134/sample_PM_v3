import { describe, expect, it } from "vitest";
import { ApiError } from "./client";
import { mapError } from "./errors";

describe("mapError", () => {
  it("maps a 404 to notFound", () => {
    expect(mapError(new ApiError(404, "nope"))).toEqual({ notFound: true, message: null });
  });

  it("maps other ApiErrors to a message", () => {
    expect(mapError(new ApiError(500, "boom"))).toEqual({ notFound: false, message: "boom" });
  });

  it("stringifies unknown errors", () => {
    expect(mapError(new Error("weird")).message).toContain("weird");
  });
});

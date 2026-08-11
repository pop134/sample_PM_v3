import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, getCurrentConditions, getHealth } from "./client";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("getHealth", () => {
  it("returns the parsed health payload", async () => {
    const payload = { status: "ok", app: "Weather Dashboard", environment: "test" };
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 })));
    const health = await getHealth();
    expect(health.status).toBe("ok");
  });

  it("throws ApiError when the response is not ok", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("error", { status: 500 })));
    await expect(getHealth()).rejects.toBeInstanceOf(ApiError);
  });
});

describe("getCurrentConditions", () => {
  it("requests the current endpoint with coordinates", async () => {
    const spy = vi.fn(async () => new Response(JSON.stringify({ id: 1 }), { status: 200 }));
    vi.stubGlobal("fetch", spy);
    await getCurrentConditions(51.5, -0.12);
    expect(String(spy.mock.calls[0][0])).toContain("/api/weather/current?lat=51.5&lon=-0.12");
  });

  it("surfaces a 404 as ApiError with status", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("no data", { status: 404 })));
    await expect(getCurrentConditions(0, 0)).rejects.toMatchObject({ status: 404 });
  });
});

import { afterEach, describe, expect, it, vi } from "vitest";
import { getHealth } from "./client";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("getHealth", () => {
  it("returns the parsed health payload", async () => {
    const payload = { status: "ok", app: "Weather Dashboard", environment: "test" };
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify(payload), { status: 200 })),
    );
    const health = await getHealth();
    expect(health.status).toBe("ok");
    expect(health.app).toBe("Weather Dashboard");
  });

  it("throws when the response is not ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response("error", { status: 500 })),
    );
    await expect(getHealth()).rejects.toThrow(/500/);
  });
});

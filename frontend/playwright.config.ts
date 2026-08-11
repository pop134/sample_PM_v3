import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright E2E config (WBS 1.7.2). Runs against the Vite dev server, which it
 * starts automatically. Run with `npm run test:e2e` (needs browsers installed
 * via `npx playwright install`). Kept out of the default CI test job.
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});

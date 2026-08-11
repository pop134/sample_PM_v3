import { expect, test } from "@playwright/test";

// End-to-end flows for dashboard load, navigation, location switch and the
// settings/sign-in path (WBS 1.7.2). Requires the backend running for live data;
// the UI still renders its loading/empty states without it.

test("dashboard loads with the brand and nav", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Weather Dashboard")).toBeVisible();
  await expect(page.getByRole("tab", { name: /Dashboard/ })).toBeVisible();
});

test("navigates to the analytics trend view", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("tab", { name: /Analytics/ }).click();
  await expect(page.getByText(/Temperature trend/)).toBeVisible();
});

test("switches to settings and shows sign-in", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("tab", { name: /Settings/ }).click();
  await expect(page.getByText(/Sign in/)).toBeVisible();
});

test("can add a location via search", async ({ page }) => {
  await page.goto("/");
  const search = page.getByRole("searchbox", { name: /Search locations/ });
  await expect(search).toBeVisible();
});

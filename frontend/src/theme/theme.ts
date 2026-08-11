// Theme resolution helpers (WBS 1.4.1). Pure and unit-tested.
export type Theme = "light" | "dark";

export const THEME_STORAGE_KEY = "weather-dashboard-theme";

export function isTheme(value: unknown): value is Theme {
  return value === "light" || value === "dark";
}

/** Choose the initial theme: stored preference, else OS preference, else light. */
export function getInitialTheme(stored: string | null, prefersDark: boolean): Theme {
  if (isTheme(stored)) return stored;
  return prefersDark ? "dark" : "light";
}

export function nextTheme(current: Theme): Theme {
  return current === "light" ? "dark" : "light";
}

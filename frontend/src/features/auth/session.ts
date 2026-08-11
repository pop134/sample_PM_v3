// Auth session persistence helpers (WBS 1.6.2). Pure/tested.
export const TOKEN_STORAGE_KEY = "weather-dashboard-token";

export function loadToken(raw: string | null): string | null {
  return raw && raw.length > 0 ? raw : null;
}

export function authHeader(token: string | null): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

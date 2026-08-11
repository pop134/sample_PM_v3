// Typed API client (WBS 1.5.1 / 1.6.2). Centralises requests, auth, query
// building and error mapping.
import { buildQuery, type QueryValue } from "./query";
import type { TrendPoint } from "../features/charts/trends";
import type {
  AccuracyResult,
  AggregateBucket,
  AlertRecord,
  AuthToken,
  AuthUser,
  LocationSummary,
  Observation,
  ObservationPage,
  Preferences,
  SavedLocationRecord,
  ThresholdRecord,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export interface Health {
  status: string;
  app: string;
  environment: string;
}

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

let authToken: string | null = null;
export function setAuthToken(token: string | null): void {
  authToken = token;
}

interface RequestInitLike {
  method?: string;
  body?: unknown;
}

export async function request<T>(
  path: string, params: Record<string, QueryValue> = {}, init: RequestInitLike = {},
): Promise<T> {
  const headers: Record<string, string> = {};
  if (authToken) headers.Authorization = `Bearer ${authToken}`;
  let body: string | undefined;
  if (init.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(init.body);
  }
  const resp = await fetch(`${BASE_URL}${path}${buildQuery(params)}`, {
    method: init.method ?? "GET", headers, body,
  });
  if (!resp.ok) {
    let detail = `Request failed: ${resp.status}`;
    try {
      const errBody = (await resp.json()) as { detail?: string };
      if (errBody?.detail) detail = errBody.detail;
    } catch {
      // non-JSON error body — keep the status message
    }
    throw new ApiError(resp.status, detail);
  }
  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

export const api = {
  health: () => request<Health>("/api/health"),
  locations: () => request<LocationSummary[]>("/api/locations"),
  current: (lat: number, lon: number, provider?: string) =>
    request<Observation>("/api/weather/current", { lat, lon, provider }),
  history: (lat: number, lon: number, opts: { limit?: number; offset?: number; start?: string; end?: string } = {}) =>
    request<ObservationPage>("/api/weather/history", { lat, lon, ...opts }),
  aggregate: (lat: number, lon: number, period = "daily") =>
    request<AggregateBucket[]>("/api/analytics/aggregate", { lat, lon, period }),
  trends: (lat: number, lon: number, period = "daily", window = 3) =>
    request<TrendPoint[]>("/api/analytics/trends", { lat, lon, period, window }),
  accuracy: (lat: number, lon: number, provider?: string) =>
    request<AccuracyResult>("/api/analytics/accuracy", { lat, lon, provider }),
  alerts: (lat: number, lon: number, severity?: string) =>
    request<AlertRecord[]>("/api/alerts", { lat, lon, severity }),

  // Auth (WBS 1.2.3 / 1.6.2)
  register: (email: string, password: string) =>
    request<AuthUser>("/api/auth/register", {}, { method: "POST", body: { email, password } }),
  login: (email: string, password: string) =>
    request<AuthToken>("/api/auth/login", {}, { method: "POST", body: { email, password } }),
  me: () => request<AuthUser>("/api/auth/me"),

  // Preferences (WBS 1.6.1)
  getPreferences: () => request<Preferences>("/api/preferences"),
  updatePreferences: (body: Partial<Preferences>) =>
    request<Preferences>("/api/preferences", {}, { method: "PUT", body }),
  savedLocations: () => request<SavedLocationRecord[]>("/api/preferences/locations"),
  addSavedLocation: (name: string, latitude: number, longitude: number) =>
    request<SavedLocationRecord>("/api/preferences/locations", {}, { method: "POST", body: { name, latitude, longitude } }),
  removeSavedLocation: (id: number) =>
    request<void>(`/api/preferences/locations/${id}`, {}, { method: "DELETE" }),
  thresholds: () => request<ThresholdRecord[]>("/api/preferences/thresholds"),
  upsertThreshold: (body: ThresholdRecord) =>
    request<ThresholdRecord>("/api/preferences/thresholds", {}, { method: "PUT", body }),
};

// Back-compat named helpers.
export const getHealth = api.health;
export const getLocations = api.locations;
export const getCurrentConditions = (lat: number, lon: number) => api.current(lat, lon);
export const getTrends = (lat: number, lon: number, period = "daily", window = 3) =>
  api.trends(lat, lon, period, window);

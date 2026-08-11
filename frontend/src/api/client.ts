// Typed API client (WBS 1.5.1). Centralises requests, query building and error
// mapping so components never touch fetch directly.
import { buildQuery, type QueryValue } from "./query";
import type { TrendPoint } from "../features/charts/trends";
import type {
  AccuracyResult,
  AggregateBucket,
  AlertRecord,
  LocationSummary,
  Observation,
  ObservationPage,
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

export async function request<T>(
  path: string, params: Record<string, QueryValue> = {},
): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}${buildQuery(params)}`);
  if (!resp.ok) {
    let detail = `Request failed: ${resp.status}`;
    try {
      const body = (await resp.json()) as { detail?: string };
      if (body?.detail) detail = body.detail;
    } catch {
      // non-JSON error body — keep the status message
    }
    throw new ApiError(resp.status, detail);
  }
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
};

// Back-compat named helpers used by existing features.
export const getHealth = api.health;
export const getLocations = api.locations;
export const getCurrentConditions = (lat: number, lon: number) => api.current(lat, lon);
export const getTrends = (lat: number, lon: number, period = "daily", window = 3) =>
  api.trends(lat, lon, period, window);

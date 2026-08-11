// Thin fetch wrapper (WBS 1.4.x). Formalised into a typed client in 1.5.1.
import type { LocationSummary, Observation } from "./types";
import type { TrendPoint } from "../features/charts/trends";

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

export async function request<T>(path: string): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`);
  if (!resp.ok) {
    throw new ApiError(resp.status, `Request failed: ${resp.status}`);
  }
  return (await resp.json()) as T;
}

export function getHealth(): Promise<Health> {
  return request<Health>("/api/health");
}

export function getCurrentConditions(lat: number, lon: number): Promise<Observation> {
  return request<Observation>(`/api/weather/current?lat=${lat}&lon=${lon}`);
}

export function getTrends(
  lat: number, lon: number, period = "daily", window = 3,
): Promise<TrendPoint[]> {
  return request<TrendPoint[]>(
    `/api/analytics/trends?lat=${lat}&lon=${lon}&period=${period}&window=${window}`,
  );
}

export function getLocations(): Promise<LocationSummary[]> {
  return request<LocationSummary[]>("/api/locations");
}

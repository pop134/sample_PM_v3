// Shared API response types mirroring the backend schemas (WBS 1.4.3 / 1.5.1).

export interface Observation {
  id: number;
  location_name: string | null;
  latitude: number;
  longitude: number;
  observed_at: string;
  temperature_c: number;
  feels_like_c: number | null;
  humidity_pct: number | null;
  pressure_hpa: number | null;
  wind_speed_ms: number | null;
  wind_deg: number | null;
  condition: string | null;
  provider: string;
}

export interface LocationSummary {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
}

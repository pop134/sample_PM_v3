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

export interface Page {
  total: number;
  limit: number;
  offset: number;
}

export interface ObservationPage {
  items: Observation[];
  page: Page;
}

export interface AggregateBucket {
  period_start: string;
  count: number;
  temp_avg: number;
  temp_min: number;
  temp_max: number;
  humidity_avg: number | null;
  wind_avg: number | null;
}

export interface AlertRecord {
  id: number;
  location_name: string | null;
  latitude: number;
  longitude: number;
  metric: string;
  value: number;
  kind: string;
  severity: string;
  message: string;
  observed_at: string;
  created_at: string;
}

export interface AccuracyResult {
  provider: string | null;
  matched: number;
  mae_c: number | null;
  bias_c: number | null;
  rmse_c: number | null;
}

// Auto-refresh configuration (WBS 1.5.4). Pure/tested.
export interface RefreshOption {
  label: string;
  ms: number | null;
}

export const REFRESH_INTERVALS: RefreshOption[] = [
  { label: "Off", ms: null },
  { label: "30s", ms: 30_000 },
  { label: "1m", ms: 60_000 },
  { label: "5m", ms: 300_000 },
];

export const DEFAULT_REFRESH_MS = 60_000;

/** The effective interval: the chosen ms while enabled, else null (paused). */
export function resolveDelay(enabled: boolean, ms: number | null): number | null {
  return enabled ? ms : null;
}

/** Human "updated N ago" label from an elapsed millisecond count. */
export function formatAgo(elapsedMs: number): string {
  const s = Math.max(0, Math.floor(elapsedMs / 1000));
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  return `${Math.floor(m / 60)}h ago`;
}

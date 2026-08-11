// Presentation formatters (WBS 1.4.1). Pure and unit-tested.

export function formatTemp(celsius: number | null | undefined, unit: "c" | "f" = "c"): string {
  if (celsius == null) return "—";
  const value = unit === "f" ? celsius * 9 / 5 + 32 : celsius;
  return `${Math.round(value * 10) / 10}°${unit.toUpperCase()}`;
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null) return "—";
  return `${Math.round(value)}%`;
}

export function formatWind(ms: number | null | undefined): string {
  if (ms == null) return "—";
  return `${Math.round(ms * 10) / 10} m/s`;
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
  });
}

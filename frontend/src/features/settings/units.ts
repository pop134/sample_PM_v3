// Unit helpers for the settings UI (WBS 1.6.2). Pure/tested.
export type TempUnit = "c" | "f";

export function isTempUnit(value: string): value is TempUnit {
  return value === "c" || value === "f";
}

export function unitLabel(unit: string): string {
  return unit === "f" ? "Fahrenheit (°F)" : "Celsius (°C)";
}

export function otherUnit(unit: TempUnit): TempUnit {
  return unit === "c" ? "f" : "c";
}

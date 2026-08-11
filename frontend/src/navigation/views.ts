// Dashboard views & navigation model (WBS 1.4.2). Pure, unit-tested.
export type ViewId = "dashboard" | "analytics" | "alerts" | "settings";

export interface ViewDef {
  id: ViewId;
  label: string;
  icon: string;
}

export const VIEWS: ViewDef[] = [
  { id: "dashboard", label: "Dashboard", icon: "🏠" },
  { id: "analytics", label: "Analytics", icon: "📈" },
  { id: "alerts", label: "Alerts", icon: "🔔" },
  { id: "settings", label: "Settings", icon: "⚙️" },
];

export const DEFAULT_VIEW: ViewId = "dashboard";

export function isViewId(value: unknown): value is ViewId {
  return VIEWS.some((v) => v.id === value);
}

import type { ReactNode } from "react";

export function DashboardGrid({ children }: { children: ReactNode }) {
  return <div className="dashboard-grid">{children}</div>;
}

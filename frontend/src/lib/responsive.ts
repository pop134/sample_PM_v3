// Responsive breakpoints & helpers (WBS 1.4.6). Pure/tested.
export const BREAKPOINTS = {
  mobile: 640,
  tablet: 1024,
} as const;

export type Breakpoint = "mobile" | "tablet" | "desktop";

export function breakpointFor(width: number): Breakpoint {
  if (width <= BREAKPOINTS.mobile) return "mobile";
  if (width <= BREAKPOINTS.tablet) return "tablet";
  return "desktop";
}

export function isMobile(width: number): boolean {
  return breakpointFor(width) === "mobile";
}

// Pure charting helpers (WBS 1.4.4). No DOM — unit-tested.

export interface Point {
  x: number;
  y: number;
}

/** Min/max of a list; returns [0, 1] for an empty list. */
export function extent(values: number[]): [number, number] {
  if (values.length === 0) return [0, 1];
  let min = values[0];
  let max = values[0];
  for (const v of values) {
    if (v < min) min = v;
    if (v > max) max = v;
  }
  if (min === max) {
    // Avoid a zero-height domain so flat series still render mid-axis.
    return [min - 1, max + 1];
  }
  return [min, max];
}

/** Linear mapping from a data domain to a pixel range. */
export function scaleLinear(
  domain: [number, number],
  range: [number, number],
): (value: number) => number {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  const span = d1 - d0 || 1;
  return (value: number) => r0 + ((value - d0) / span) * (r1 - r0);
}

/** SVG path ("M x y L x y …") through the given points. */
export function buildLinePath(points: Point[]): string {
  if (points.length === 0) return "";
  return points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${round(p.x)} ${round(p.y)}`)
    .join(" ");
}

function round(n: number): number {
  return Math.round(n * 100) / 100;
}

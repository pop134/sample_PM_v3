import { useEffect, useRef } from "react";

/**
 * Call `callback` every `delayMs`. A null delay pauses the timer. The latest
 * callback is always used without resetting the interval (WBS 1.5.4).
 */
export function useInterval(callback: () => void, delayMs: number | null): void {
  const saved = useRef(callback);

  useEffect(() => {
    saved.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delayMs === null) return;
    const id = setInterval(() => saved.current(), delayMs);
    return () => clearInterval(id);
  }, [delayMs]);
}

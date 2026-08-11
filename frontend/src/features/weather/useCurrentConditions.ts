import { useEffect, useState } from "react";
import { ApiError, getCurrentConditions } from "../../api/client";
import type { Observation } from "../../api/types";

export interface CurrentState {
  data: Observation | null;
  loading: boolean;
  error: string | null;
  notFound: boolean;
}

export function useCurrentConditions(lat: number, lon: number): CurrentState {
  const [state, setState] = useState<CurrentState>({
    data: null, loading: true, error: null, notFound: false,
  });

  useEffect(() => {
    let active = true;
    setState({ data: null, loading: true, error: null, notFound: false });
    getCurrentConditions(lat, lon)
      .then((data) => active && setState({ data, loading: false, error: null, notFound: false }))
      .catch((e: unknown) => {
        if (!active) return;
        const notFound = e instanceof ApiError && e.status === 404;
        setState({ data: null, loading: false, notFound, error: notFound ? null : String(e) });
      });
    return () => {
      active = false;
    };
  }, [lat, lon]);

  return state;
}

// Default location until saved locations (1.6.1) drive selection.
export const DEFAULT_LOCATION = { lat: 51.5074, lon: -0.1278, name: "London" };

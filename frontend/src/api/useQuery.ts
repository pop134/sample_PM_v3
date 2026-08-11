import { useEffect, useState } from "react";
import { mapError } from "./errors";

export interface QueryState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  notFound: boolean;
}

export interface QueryResult<T> extends QueryState<T> {
  refetch: () => void;
}

/**
 * Generic data-fetching hook: runs `fetcher` when `deps` change, tracking
 * loading / error / notFound(404), cancelling stale requests, and exposing
 * `refetch`. Centralises the pattern the widgets previously repeated.
 */
export function useQuery<T>(fetcher: () => Promise<T>, deps: unknown[]): QueryResult<T> {
  const [state, setState] = useState<QueryState<T>>({
    data: null, loading: true, error: null, notFound: false,
  });
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    let active = true;
    setState((s) => ({ ...s, loading: true, error: null, notFound: false }));
    fetcher()
      .then((data) => {
        if (active) setState({ data, loading: false, error: null, notFound: false });
      })
      .catch((e: unknown) => {
        if (!active) return;
        const mapped = mapError(e);
        setState({ data: null, loading: false, notFound: mapped.notFound, error: mapped.message });
      });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  return { ...state, refetch: () => setNonce((n) => n + 1) };
}

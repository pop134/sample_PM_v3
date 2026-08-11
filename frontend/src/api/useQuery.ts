import { useEffect, useState } from "react";
import { queryCache } from "./cache";
import { mapError } from "./errors";
import { cachedState, type QueryState } from "./queryState";

export type { QueryState } from "./queryState";

export interface QueryResult<T> extends QueryState<T> {
  refetch: () => void;
}

interface QueryOptions {
  /** When set, results are cached and served cache-first with revalidation. */
  cacheKey?: string;
}

/**
 * Generic data-fetching hook (WBS 1.5.1/1.5.2). Runs `fetcher` on `deps` change,
 * tracks loading/error/notFound, cancels stale requests, and — when `cacheKey`
 * is given — serves a cached value immediately while revalidating in the
 * background if the entry is missing or stale. `refetch` invalidates + refetches.
 */
export function useQuery<T>(
  fetcher: () => Promise<T>, deps: unknown[], options: QueryOptions = {},
): QueryResult<T> {
  const { cacheKey } = options;
  const [state, setState] = useState<QueryState<T>>(() =>
    cachedState<T>(cacheKey ? queryCache.get<T>(cacheKey) : undefined),
  );
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    let active = true;
    const cached = cacheKey ? queryCache.get<T>(cacheKey) : undefined;
    if (cached !== undefined) {
      setState({ data: cached.value, loading: false, error: null, notFound: false });
    } else {
      setState((s) => ({ ...s, loading: true, error: null, notFound: false }));
    }

    const shouldFetch = !cacheKey || cached === undefined || queryCache.isStale(cacheKey);
    if (shouldFetch) {
      fetcher()
        .then((data) => {
          if (!active) return;
          if (cacheKey) queryCache.set(cacheKey, data);
          setState({ data, loading: false, error: null, notFound: false });
        })
        .catch((e: unknown) => {
          if (!active) return;
          const mapped = mapError(e);
          // Keep any stale data visible when a revalidation fails.
          setState((prev) => ({
            data: prev.data, loading: false, notFound: mapped.notFound, error: mapped.message,
          }));
        });
    }
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  const refetch = () => {
    if (cacheKey) queryCache.invalidate(cacheKey);
    setNonce((n) => n + 1);
  };

  return { ...state, refetch };
}

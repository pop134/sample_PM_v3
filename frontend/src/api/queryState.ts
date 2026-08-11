// Initial query state derivation (WBS 1.5.2). Pure/tested.
import type { CacheEntry } from "./cache";

export interface QueryState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  notFound: boolean;
}

/** Seed state from cache: cached value renders immediately (not loading). */
export function cachedState<T>(entry: CacheEntry<T> | undefined): QueryState<T> {
  if (entry !== undefined) {
    return { data: entry.value, loading: false, error: null, notFound: false };
  }
  return { data: null, loading: true, error: null, notFound: false };
}

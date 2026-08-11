// Client-side query cache (WBS 1.5.2). Framework-free; clock injectable for tests.
export interface CacheEntry<T> {
  value: T;
  storedAt: number;
}

export class QueryCache {
  private store = new Map<string, CacheEntry<unknown>>();

  constructor(
    private readonly ttlMs: number,
    private readonly clock: () => number = () => Date.now(),
  ) {}

  get<T>(key: string): CacheEntry<T> | undefined {
    return this.store.get(key) as CacheEntry<T> | undefined;
  }

  set<T>(key: string, value: T): void {
    this.store.set(key, { value, storedAt: this.clock() });
  }

  /** True when there is no entry or it is older than the TTL. */
  isStale(key: string): boolean {
    const entry = this.store.get(key);
    if (entry === undefined) return true;
    return this.clock() - entry.storedAt >= this.ttlMs;
  }

  invalidate(key?: string): void {
    if (key === undefined) this.store.clear();
    else this.store.delete(key);
  }

  get size(): number {
    return this.store.size;
  }
}

// Shared 30s cache used by the data-fetching hook.
export const queryCache = new QueryCache(30_000);

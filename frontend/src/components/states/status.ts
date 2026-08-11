// Derive a single render status from a query state (WBS 1.5.3). Pure/tested.
export type ViewStatus = "loading" | "error" | "empty" | "ready";

export interface QueryLike<T> {
  loading: boolean;
  error: string | null;
  notFound: boolean;
  data: T | null;
}

/**
 * Collapse a query state into one status a widget can switch on. `isEmpty`
 * lets callers treat an otherwise-successful-but-blank result as empty.
 */
export function viewStatus<T>(
  state: QueryLike<T>, isEmpty?: (data: T) => boolean,
): ViewStatus {
  if (state.error) return "error";
  if (state.notFound) return "empty";
  if (state.data !== null) {
    return isEmpty && isEmpty(state.data) ? "empty" : "ready";
  }
  if (state.loading) return "loading";
  return "empty";
}

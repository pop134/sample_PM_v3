// Error mapping for data-fetching (WBS 1.5.1). Pure/tested.
import { ApiError } from "./client";

export interface MappedError {
  notFound: boolean;
  message: string | null;
}

export function mapError(error: unknown): MappedError {
  if (error instanceof ApiError) {
    if (error.status === 404) return { notFound: true, message: null };
    return { notFound: false, message: error.message };
  }
  return { notFound: false, message: String(error) };
}

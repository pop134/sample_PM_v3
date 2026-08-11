// Thin fetch wrapper. Replaced by a typed, generated client under WBS 1.5.1.
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export interface Health {
  status: string;
  app: string;
  environment: string;
}

async function request<T>(path: string): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`);
  if (!resp.ok) {
    throw new Error(`Request failed: ${resp.status}`);
  }
  return (await resp.json()) as T;
}

export function getHealth(): Promise<Health> {
  return request<Health>("/api/health");
}

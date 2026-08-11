import { getCurrentConditions } from "../../api/client";
import { useQuery, type QueryResult } from "../../api/useQuery";
import type { Observation } from "../../api/types";

export function useCurrentConditions(lat: number, lon: number): QueryResult<Observation> {
  return useQuery<Observation>(() => getCurrentConditions(lat, lon), [lat, lon]);
}

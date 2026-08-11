import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { LocationSummary } from "../../api/types";
import { addLocation, removeLocation } from "./search";
import {
  DEFAULT_LOCATIONS,
  LOCATIONS_STORAGE_KEY,
  parseLocations,
  serializeLocations,
} from "./state";

interface LocationContextValue {
  locations: LocationSummary[];
  active: LocationSummary;
  activeId: number;
  select: (loc: LocationSummary) => void;
  setActive: (id: number) => void;
  remove: (id: number) => void;
}

const LocationContext = createContext<LocationContextValue | undefined>(undefined);

function readInitial(): LocationSummary[] {
  if (typeof window === "undefined") return DEFAULT_LOCATIONS;
  return parseLocations(window.localStorage.getItem(LOCATIONS_STORAGE_KEY));
}

export function LocationProvider({ children }: { children: ReactNode }) {
  const [locations, setLocations] = useState<LocationSummary[]>(readInitial);
  const [activeId, setActiveId] = useState<number>(() => readInitial()[0].id);

  useEffect(() => {
    window.localStorage.setItem(LOCATIONS_STORAGE_KEY, serializeLocations(locations));
  }, [locations]);

  const select = useCallback((loc: LocationSummary) => {
    setLocations((prev) => addLocation(prev, loc));
    setActiveId(loc.id);
  }, []);

  const remove = useCallback((id: number) => {
    setLocations((prev) => {
      const next = removeLocation(prev, id);
      return next.length > 0 ? next : DEFAULT_LOCATIONS;
    });
  }, []);

  const active = useMemo(
    () => locations.find((l) => l.id === activeId) ?? locations[0],
    [locations, activeId],
  );

  const value: LocationContextValue = {
    locations, active, activeId: active.id, select, setActive: setActiveId, remove,
  };
  return <LocationContext.Provider value={value}>{children}</LocationContext.Provider>;
}

export function useLocations(): LocationContextValue {
  const ctx = useContext(LocationContext);
  if (ctx === undefined) {
    throw new Error("useLocations must be used within a LocationProvider");
  }
  return ctx;
}

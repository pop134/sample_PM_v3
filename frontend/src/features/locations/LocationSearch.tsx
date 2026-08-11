import { useEffect, useMemo, useState } from "react";
import { getLocations } from "../../api/client";
import type { LocationSummary } from "../../api/types";
import { filterLocations } from "./search";

interface LocationSearchProps {
  onSelect: (location: LocationSummary) => void;
}

export function LocationSearch({ onSelect }: LocationSearchProps) {
  const [all, setAll] = useState<LocationSummary[]>([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    let active = true;
    getLocations()
      .then((l) => active && setAll(l))
      .catch(() => active && setAll([]));
    return () => {
      active = false;
    };
  }, []);

  const results = useMemo(() => filterLocations(all, query).slice(0, 8), [all, query]);

  return (
    <div className="loc-search">
      <input
        className="loc-search__input"
        type="search"
        placeholder="Search locations…"
        aria-label="Search locations"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      {query && (
        <ul className="loc-search__results">
          {results.length === 0 && <li className="muted loc-search__empty">No matches</li>}
          {results.map((loc) => (
            <li key={loc.id}>
              <button className="loc-search__item" onClick={() => { onSelect(loc); setQuery(""); }}>
                {loc.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

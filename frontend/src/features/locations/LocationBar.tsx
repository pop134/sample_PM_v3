import { LocationSearch } from "./LocationSearch";
import { useLocations } from "./LocationContext";

export function LocationBar() {
  const { locations, activeId, select, setActive, remove } = useLocations();
  return (
    <div className="loc-bar">
      <div className="loc-bar__chips" role="group" aria-label="Saved locations">
        {locations.map((loc) => (
          <span key={loc.id} className={`loc-chip${loc.id === activeId ? " loc-chip--active" : ""}`}>
            <button className="loc-chip__name" onClick={() => setActive(loc.id)} aria-pressed={loc.id === activeId}>
              {loc.name}
            </button>
            <button className="loc-chip__remove" aria-label={`Remove ${loc.name}`} onClick={() => remove(loc.id)}>
              ×
            </button>
          </span>
        ))}
      </div>
      <LocationSearch onSelect={select} />
    </div>
  );
}

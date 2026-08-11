import { useCallback, useEffect, useState } from "react";
import { api } from "../../api/client";
import type { SavedLocationRecord } from "../../api/types";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { EmptyState } from "../../components/states/EmptyState";
import { useLocations } from "../locations/LocationContext";

export function SavedLocationsPanel() {
  const { active } = useLocations();
  const [saved, setSaved] = useState<SavedLocationRecord[]>([]);

  const reload = useCallback(() => {
    api.savedLocations().then(setSaved).catch(() => setSaved([]));
  }, []);

  useEffect(() => { reload(); }, [reload]);

  const addCurrent = async () => {
    await api.addSavedLocation(active.name, active.latitude, active.longitude);
    reload();
  };

  const remove = async (id: number) => {
    await api.removeSavedLocation(id);
    reload();
  };

  return (
    <Card title="Saved locations">
      <Button onClick={addCurrent}>Save “{active.name}”</Button>
      {saved.length === 0 ? (
        <EmptyState message="No saved locations yet." icon="📍" />
      ) : (
        <ul className="saved-list">
          {saved.map((loc) => (
            <li key={loc.id} className="saved-list__item">
              <span>{loc.name}</span>
              <Button variant="ghost" onClick={() => remove(loc.id)} aria-label={`Remove ${loc.name}`}>Remove</Button>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

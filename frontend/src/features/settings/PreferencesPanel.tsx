import { useEffect, useState } from "react";
import { api } from "../../api/client";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";
import { isTempUnit, unitLabel, type TempUnit } from "./units";

export function PreferencesPanel() {
  const [unit, setUnit] = useState<TempUnit>("c");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.getPreferences().then((p) => {
      if (isTempUnit(p.temperature_unit)) setUnit(p.temperature_unit);
    }).catch(() => undefined);
  }, []);

  const change = async (next: TempUnit) => {
    setUnit(next);
    setSaving(true);
    try {
      await api.updatePreferences({ temperature_unit: next });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card title="Units">
      <p className="muted">Temperature unit: {unitLabel(unit)}{saving ? " (saving…)" : ""}</p>
      <div className="refresh" role="group" aria-label="Temperature unit">
        {(["c", "f"] as TempUnit[]).map((u) => (
          <Button key={u} variant={u === unit ? "primary" : "ghost"} onClick={() => change(u)}>
            {u === "c" ? "°C" : "°F"}
          </Button>
        ))}
      </div>
    </Card>
  );
}

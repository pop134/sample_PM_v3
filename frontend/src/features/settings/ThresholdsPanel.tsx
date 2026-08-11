import { useCallback, useEffect, useState } from "react";
import { api } from "../../api/client";
import type { ThresholdRecord } from "../../api/types";
import { Button } from "../../components/Button";
import { Card } from "../../components/Card";

const METRICS = ["temperature_c", "wind_speed_ms", "humidity_pct"];

export function ThresholdsPanel() {
  const [rows, setRows] = useState<ThresholdRecord[]>([]);
  const [metric, setMetric] = useState(METRICS[0]);
  const [maximum, setMaximum] = useState("");

  const reload = useCallback(() => {
    api.thresholds().then(setRows).catch(() => setRows([]));
  }, []);

  useEffect(() => { reload(); }, [reload]);

  const save = async () => {
    await api.upsertThreshold({
      metric,
      minimum: null,
      maximum: maximum === "" ? null : Number(maximum),
      severity: "warning",
    });
    setMaximum("");
    reload();
  };

  return (
    <Card title="Alert thresholds">
      <div className="threshold-form">
        <select className="loc-search__input" value={metric} onChange={(e) => setMetric(e.target.value)} aria-label="Metric">
          {METRICS.map((m) => <option key={m} value={m}>{m}</option>)}
        </select>
        <input className="loc-search__input" type="number" placeholder="Max" value={maximum}
          onChange={(e) => setMaximum(e.target.value)} aria-label="Maximum" />
        <Button onClick={save}>Set</Button>
      </div>
      <ul className="saved-list">
        {rows.map((t) => (
          <li key={t.metric} className="saved-list__item">
            <span>{t.metric}</span>
            <span className="muted">max {t.maximum ?? "—"} · {t.severity}</span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

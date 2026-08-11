import { REFRESH_INTERVALS } from "./refresh";

interface AutoRefreshControlProps {
  value: number | null;
  onChange: (ms: number | null) => void;
}

export function AutoRefreshControl({ value, onChange }: AutoRefreshControlProps) {
  return (
    <div className="refresh" role="group" aria-label="Auto-refresh interval">
      <span className="refresh__label muted">Auto-refresh</span>
      {REFRESH_INTERVALS.map((opt) => (
        <button
          key={opt.label}
          className={`nav__item${opt.ms === value ? " nav__item--active" : ""}`}
          aria-pressed={opt.ms === value}
          onClick={() => onChange(opt.ms)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

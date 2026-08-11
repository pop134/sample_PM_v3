interface SpinnerProps {
  label?: string;
}

export function Spinner({ label = "Loading…" }: SpinnerProps) {
  return (
    <div className="ui-spinner" role="status" aria-live="polite">
      <span className="ui-spinner__dot" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

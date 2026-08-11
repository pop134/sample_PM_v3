interface EmptyStateProps {
  message?: string;
  icon?: string;
}

export function EmptyState({ message = "Nothing to show yet.", icon = "🗒️" }: EmptyStateProps) {
  return (
    <div className="state state--empty">
      <span className="state__icon" aria-hidden="true">{icon}</span>
      <p className="muted">{message}</p>
    </div>
  );
}

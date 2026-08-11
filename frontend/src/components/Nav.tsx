import { VIEWS, type ViewId } from "../navigation/views";

interface NavProps {
  active: ViewId;
  onSelect: (id: ViewId) => void;
}

export function Nav({ active, onSelect }: NavProps) {
  return (
    <ul className="nav" role="tablist">
      {VIEWS.map((view) => (
        <li key={view.id}>
          <button
            role="tab"
            aria-selected={active === view.id}
            className={`nav__item${active === view.id ? " nav__item--active" : ""}`}
            onClick={() => onSelect(view.id)}
          >
            <span aria-hidden="true">{view.icon}</span> {view.label}
          </button>
        </li>
      ))}
    </ul>
  );
}

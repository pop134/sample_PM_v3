import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  children: ReactNode;
  className?: string;
}

export function Card({ title, children, className }: CardProps) {
  return (
    <section className={`ui-card${className ? ` ${className}` : ""}`}>
      {title && <h3 className="ui-card__title">{title}</h3>}
      <div className="ui-card__body">{children}</div>
    </section>
  );
}

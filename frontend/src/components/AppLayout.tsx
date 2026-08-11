import type { ReactNode } from "react";
import { ThemeToggle } from "./ThemeToggle";

interface AppLayoutProps {
  nav?: ReactNode;
  children: ReactNode;
}

export function AppLayout({ nav, children }: AppLayoutProps) {
  return (
    <div className="layout">
      <header className="layout__header">
        <div className="layout__brand">
          <span className="layout__logo" aria-hidden="true">⛅</span>
          <span>Weather Dashboard</span>
        </div>
        <ThemeToggle />
      </header>
      {nav && <nav className="layout__nav">{nav}</nav>}
      <main className="layout__main">{children}</main>
    </div>
  );
}

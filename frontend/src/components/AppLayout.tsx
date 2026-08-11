import { useState } from "react";
import type { ReactNode } from "react";
import { isNavVisible } from "../lib/responsive";
import { useMediaQuery } from "../lib/useMediaQuery";
import { BREAKPOINTS } from "../lib/responsive";
import { ThemeToggle } from "./ThemeToggle";

interface AppLayoutProps {
  nav?: ReactNode;
  children: ReactNode;
}

export function AppLayout({ nav, children }: AppLayoutProps) {
  const isMobileView = useMediaQuery(`(max-width: ${BREAKPOINTS.mobile}px)`);
  const [open, setOpen] = useState(false);
  const showNav = nav != null && isNavVisible(isMobileView, open);

  return (
    <div className="layout">
      <header className="layout__header">
        <div className="layout__brand">
          <span className="layout__logo" aria-hidden="true">⛅</span>
          <span>Weather Dashboard</span>
        </div>
        <div className="layout__actions">
          {nav && isMobileView && (
            <button
              className="ui-btn ui-btn--ghost layout__menu"
              aria-expanded={open}
              aria-controls="app-nav"
              onClick={() => setOpen((o) => !o)}
            >
              ☰ Menu
            </button>
          )}
          <ThemeToggle />
        </div>
      </header>
      {showNav && (
        <nav id="app-nav" className="layout__nav">
          {nav}
        </nav>
      )}
      <main className="layout__main">{children}</main>
    </div>
  );
}

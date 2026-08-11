import { useTheme } from "../theme/ThemeContext";
import { Button } from "./Button";

export function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <Button variant="ghost" onClick={toggle} aria-label="Toggle colour theme">
      {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
    </Button>
  );
}

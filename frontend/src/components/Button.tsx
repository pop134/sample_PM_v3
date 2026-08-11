import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
}

export function Button({ variant = "primary", className, ...rest }: ButtonProps) {
  return <button className={`ui-btn ui-btn--${variant}${className ? ` ${className}` : ""}`} {...rest} />;
}

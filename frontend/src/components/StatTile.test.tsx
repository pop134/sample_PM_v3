import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatTile } from "./StatTile";

describe("StatTile", () => {
  it("renders label, value and optional hint", () => {
    render(<StatTile label="Temperature" value="20°C" hint="feels like 19°C" />);
    expect(screen.getByText("Temperature")).toBeTruthy();
    expect(screen.getByText("20°C")).toBeTruthy();
    expect(screen.getByText("feels like 19°C")).toBeTruthy();
  });
});

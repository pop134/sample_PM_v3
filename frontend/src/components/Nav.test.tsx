import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Nav } from "./Nav";

describe("Nav", () => {
  it("marks the active tab and reports selection", () => {
    const onSelect = vi.fn();
    render(<Nav active="dashboard" onSelect={onSelect} />);
    const analytics = screen.getByRole("tab", { name: /Analytics/ });
    fireEvent.click(analytics);
    expect(onSelect).toHaveBeenCalledWith("analytics");

    const dashboard = screen.getByRole("tab", { name: /Dashboard/ });
    expect(dashboard.getAttribute("aria-selected")).toBe("true");
  });
});

import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";

// Unmount React trees between tests to keep the DOM isolated.
afterEach(() => {
  cleanup();
});

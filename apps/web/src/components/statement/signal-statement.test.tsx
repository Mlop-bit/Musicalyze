import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it } from "vitest";
import type { SignalStatement as SignalStatementComponent } from "./signal-statement";

function ensureMatchMedia() {
  if (typeof window.matchMedia === "function") return;
  window.matchMedia = ((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  })) as unknown as typeof window.matchMedia;
}

let SignalStatement: typeof SignalStatementComponent;

beforeAll(async () => {
  ensureMatchMedia();
  ({ SignalStatement } = await import("./signal-statement"));
});

afterEach(cleanup);

describe("SignalStatement", () => {
  it("renders the heading", () => {
    render(<SignalStatement />);
    expect(
      screen.getByRole("heading", { name: /the signal never stopped/i }),
    ).toBeInTheDocument();
  });

  it("renders the pull-quote sentences", () => {
    render(<SignalStatement />);
    expect(
      screen.getByText(/spotify shut off the endpoints/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/musicalyze rebuilds that layer/i),
    ).toBeInTheDocument();
  });
});

import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it } from "vitest";
import type { PipelineStrip as PipelineStripComponent } from "./pipeline-strip";

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

let PipelineStrip: typeof PipelineStripComponent;

beforeAll(async () => {
  ensureMatchMedia();
  ({ PipelineStrip } = await import("./pipeline-strip"));
});

afterEach(cleanup);

describe("PipelineStrip", () => {
  it("renders the rebuild-pipeline heading", () => {
    render(<PipelineStrip />);
    expect(
      screen.getAllByRole("heading", {
        name: /how the missing metadata gets rebuilt/i,
      }).length,
    ).toBeGreaterThan(0);
  });

  it("renders every stage label", () => {
    render(<PipelineStrip />);
    expect(screen.getAllByText("Spotify gap").length).toBeGreaterThan(0);
    expect(screen.getAllByText("MuQ model").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Segmentation & recs").length).toBeGreaterThan(
      0,
    );
  });
});

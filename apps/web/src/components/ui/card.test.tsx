import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Card, CardContent, CardDescription, CardTitle } from "./card";

afterEach(cleanup);

describe("Card", () => {
  beforeEach(() => {
    let callback: ResizeObserverCallback = () => {};
    vi.stubGlobal(
      "ResizeObserver",
      class {
        constructor(cb: ResizeObserverCallback) {
          callback = cb;
        }
        observe(target: Element) {
          callback(
            [
              {
                target,
                contentRect: { width: 320, height: 160 },
                borderBoxSize: [{ inlineSize: 320, blockSize: 160 }],
              } as unknown as ResizeObserverEntry,
            ],
            this as unknown as ResizeObserver,
          );
        }
        disconnect() {}
        unobserve() {}
      },
    );
  });

  it("renders its content", () => {
    render(
      <Card>
        <CardTitle>Listening habits</CardTitle>
        <CardDescription>Last 30 days</CardDescription>
        <CardContent>128 tracks analyzed</CardContent>
      </Card>,
    );

    expect(screen.getByText("Listening habits")).toBeInTheDocument();
    expect(screen.getByText("128 tracks analyzed")).toBeInTheDocument();
  });

  it("draws a squircle path once it measures its size", () => {
    const { container } = render(
      <Card>
        <CardContent>Hello</CardContent>
      </Card>,
    );

    const path = container.querySelector("path");
    expect(path).not.toBeNull();
    expect(path?.getAttribute("d")).toBeTruthy();
  });
});

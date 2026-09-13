import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { formatRelativeDate } from "./format-relative-date";

beforeEach(() => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-09-09T12:00:00Z"));
});

afterEach(() => {
  vi.useRealTimers();
});

describe("formatRelativeDate", () => {
  it("formats minutes", () => {
    expect(formatRelativeDate("2026-09-09T11:45:00Z")).toBe("15m ago");
  });

  it("formats hours", () => {
    expect(formatRelativeDate("2026-09-09T06:00:00Z")).toBe("6h ago");
  });

  it("formats days", () => {
    expect(formatRelativeDate("2026-09-05T12:00:00Z")).toBe("4d ago");
  });
});

import { describe, expect, it } from "vitest";
import { moodColor, normalizeLevels } from "./mood-color";

describe("normalizeLevels", () => {
  it("scales known values to the 0 to 1 range and keeps unknowns", () => {
    expect(normalizeLevels([-0.5, null, 0.5])).toEqual([0, null, 1]);
  });

  it("centres a flat list", () => {
    expect(normalizeLevels([0.2, 0.2])).toEqual([0.5, 0.5]);
  });

  it("returns unknowns when nothing is known", () => {
    expect(normalizeLevels([null, null])).toEqual([null, null]);
  });
});

describe("moodColor", () => {
  it("runs from blue for calm to green for energetic", () => {
    expect(moodColor(0)).toBe("hsl(205 78% 52%)");
    expect(moodColor(1)).toBe("hsl(115 78% 52%)");
  });

  it("clamps out of range levels", () => {
    expect(moodColor(2)).toBe(moodColor(1));
  });
});

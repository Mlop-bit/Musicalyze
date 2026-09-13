import { describe, expect, it } from "vitest";
import { computeTimelinePositions } from "./timeline-positions";

function daysAgo(days: number): string {
  return new Date(Date.now() - days * 86_400_000).toISOString();
}

describe("computeTimelinePositions", () => {
  it("orders positions monotonically from newest (smallest y) to oldest (largest y)", () => {
    const layout = computeTimelinePositions([
      [
        { id: "a", date: daysAgo(10) },
        { id: "b", date: daysAgo(0) },
        { id: "c", date: daysAgo(5) },
      ],
    ]);

    const byId = new Map(layout.branches[0].map((p) => [p.id, p.y]));
    expect(byId.get("b")!).toBeLessThan(byId.get("c")!);
    expect(byId.get("c")!).toBeLessThan(byId.get("a")!);
  });

  it("enforces a minimum gap between consecutive points on the same branch", () => {
    const minGapPx = 72;
    const layout = computeTimelinePositions(
      [
        [
          { id: "a", date: daysAgo(0) },
          { id: "b", date: daysAgo(0.001) },
          { id: "c", date: daysAgo(0.002) },
        ],
      ],
      { minGapPx },
    );

    const positions = layout.branches[0].sort((x, y) => x.y - y.y);
    for (let i = 1; i < positions.length; i += 1) {
      expect(positions[i].y - positions[i - 1].y).toBeGreaterThanOrEqual(
        minGapPx,
      );
    }
  });

  it("never produces two points at the same y on the same branch even for identical dates", () => {
    const sameDate = daysAgo(3);
    const layout = computeTimelinePositions([
      [
        { id: "a", date: sameDate },
        { id: "b", date: sameDate },
        { id: "c", date: sameDate },
      ],
    ]);

    const ys = layout.branches[0].map((p) => p.y);
    expect(new Set(ys).size).toBe(ys.length);
  });

  it("covers the furthest point with the total track height", () => {
    const edgePaddingPx = 40;
    const layout = computeTimelinePositions(
      [[{ id: "a", date: daysAgo(0) }], [{ id: "b", date: daysAgo(100) }]],
      { edgePaddingPx },
    );

    const furthestY = Math.max(...layout.branches.flat().map((p) => p.y));
    expect(layout.trackHeight).toBeGreaterThanOrEqual(
      furthestY + edgePaddingPx,
    );
    expect(layout.trackHeight).toBe(furthestY + edgePaddingPx);
  });

  it("aligns commits from different branches on the same day to roughly the same height", () => {
    const sharedDate = daysAgo(7);
    const layout = computeTimelinePositions([
      [{ id: "release-1", date: sharedDate }],
      [{ id: "dev-1", date: sharedDate }],
    ]);

    const releaseY = layout.branches[0][0].y;
    const devY = layout.branches[1][0].y;
    expect(releaseY).toBe(devY);
  });

  it("returns an empty layout with a minimal track height when there are no entries", () => {
    const layout = computeTimelinePositions([[], []], { edgePaddingPx: 40 });
    expect(layout.branches).toEqual([[], []]);
    expect(layout.trackHeight).toBe(80);
  });

  it("handles one branch being empty while the other has entries", () => {
    const layout = computeTimelinePositions([
      [],
      [{ id: "dev-1", date: daysAgo(1) }],
    ]);

    expect(layout.branches[0]).toEqual([]);
    expect(layout.branches[1]).toHaveLength(1);
    expect(layout.trackHeight).toBeGreaterThan(0);
  });
});

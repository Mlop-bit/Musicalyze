export type TimelineDatedEntry = {
  id: string;
  date: string;
};

export type TimelinePosition = {
  id: string;
  y: number;
};

export type TimelineLayout = {
  branches: TimelinePosition[][];
  trackHeight: number;
};

export type TimelinePositionOptions = {
  pixelsPerDay?: number;
  minGapPx?: number;
  edgePaddingPx?: number;
};

export const DEFAULT_PIXELS_PER_DAY = 56;
export const DEFAULT_MIN_GAP_PX = 88;
export const DEFAULT_EDGE_PADDING_PX = 40;

const MS_PER_DAY = 86_400_000;

export function computeTimelinePositions(
  branches: TimelineDatedEntry[][],
  options: TimelinePositionOptions = {},
): TimelineLayout {
  const pixelsPerDay = options.pixelsPerDay ?? DEFAULT_PIXELS_PER_DAY;
  const minGapPx = options.minGapPx ?? DEFAULT_MIN_GAP_PX;
  const edgePaddingPx = options.edgePaddingPx ?? DEFAULT_EDGE_PADDING_PX;

  const allEntries = branches.flat();

  if (allEntries.length === 0) {
    return {
      branches: branches.map(() => []),
      trackHeight: edgePaddingPx * 2,
    };
  }

  const newestTime = Math.max(
    ...allEntries.map((entry) => new Date(entry.date).getTime()),
  );

  let trackHeight = edgePaddingPx * 2;

  const layoutBranches = branches.map((entries) => {
    const sorted = [...entries].sort(
      (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime(),
    );

    let previousY: number | null = null;
    const positions: TimelinePosition[] = [];

    for (const entry of sorted) {
      const ageDays =
        (newestTime - new Date(entry.date).getTime()) / MS_PER_DAY;
      const rawY = edgePaddingPx + ageDays * pixelsPerDay;
      const y: number =
        previousY === null ? rawY : Math.max(rawY, previousY + minGapPx);
      previousY = y;
      positions.push({ id: entry.id, y });
      trackHeight = Math.max(trackHeight, y + edgePaddingPx);
    }

    return positions;
  });

  return { branches: layoutBranches, trackHeight };
}

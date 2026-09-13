"use client";

import { useMemo, useRef, useState } from "react";
import { computeTimelinePositions } from "@/lib/timeline-positions";
import type { CommitEntry } from "@/server/github/schema";
import { DEVELOPMENT_THEME, RELEASE_THEME } from "./changelog-themes";
import { TimelineRail } from "./timeline-rail";
import { useTimelineCardSpacing } from "./use-timeline-card-spacing";
import { useTimelineScroll } from "./use-timeline-scroll";

export type VerticalTimelineProps = {
  releases: CommitEntry[];
  commits: CommitEntry[];
  releaseCompareUrl: string;
  developmentCompareUrl: string;
};

export function VerticalTimeline({
  releases,
  commits,
  releaseCompareUrl,
  developmentCompareUrl,
}: VerticalTimelineProps) {
  const releaseTrackRef = useRef<HTMLDivElement | null>(null);
  const developmentTrackRef = useRef<HTMLDivElement | null>(null);
  const releasePathRef = useRef<SVGPathElement | null>(null);
  const developmentPathRef = useRef<SVGPathElement | null>(null);
  const releaseCardRefs = useRef<Map<string, HTMLElement>>(new Map());
  const developmentCardRefs = useRef<Map<string, HTMLElement>>(new Map());

  const [minGapOverride, setMinGapOverride] = useState<number | undefined>(
    undefined,
  );
  const [edgePaddingOverride, setEdgePaddingOverride] = useState<
    number | undefined
  >(undefined);

  const layout = useMemo(
    () =>
      computeTimelinePositions(
        [
          releases.map((entry) => ({ id: entry.sha, date: entry.date })),
          commits.map((entry) => ({ id: entry.sha, date: entry.date })),
        ],
        { minGapPx: minGapOverride, edgePaddingPx: edgePaddingOverride },
      ),
    [releases, commits, minGapOverride, edgePaddingOverride],
  );

  const releasePositions = useMemo(
    () =>
      new Map(layout.branches[0].map((position) => [position.id, position.y])),
    [layout],
  );
  const developmentPositions = useMemo(
    () =>
      new Map(layout.branches[1].map((position) => [position.id, position.y])),
    [layout],
  );

  useTimelineCardSpacing({
    releaseCardRefs,
    developmentCardRefs,
    layoutKey: layout,
    setMinGapOverride,
    setEdgePaddingOverride,
  });

  useTimelineScroll({
    releaseTrackRef,
    developmentTrackRef,
    releasePathRef,
    developmentPathRef,
    releaseCardRefs,
    developmentCardRefs,
    layoutKey: layout,
  });

  return (
    <div className="relative">
      <div className="grid grid-cols-2 gap-4 sm:gap-8 md:gap-16">
        <TimelineRail
          theme={RELEASE_THEME}
          entries={releases}
          positions={releasePositions}
          trackHeight={layout.trackHeight}
          trackRef={releaseTrackRef}
          pathRef={releasePathRef}
          cardRefs={releaseCardRefs}
          compareUrl={releaseCompareUrl}
        />
        <TimelineRail
          theme={DEVELOPMENT_THEME}
          entries={commits}
          positions={developmentPositions}
          trackHeight={layout.trackHeight}
          trackRef={developmentTrackRef}
          pathRef={developmentPathRef}
          cardRefs={developmentCardRefs}
          compareUrl={developmentCompareUrl}
        />
      </div>
    </div>
  );
}

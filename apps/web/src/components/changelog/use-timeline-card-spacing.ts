import { useLayoutEffect } from "react";
import {
  DEFAULT_EDGE_PADDING_PX,
  DEFAULT_MIN_GAP_PX,
} from "@/lib/timeline-positions";

const CARD_HEIGHT_BUFFER_PX = 8;

type MutableRef<T> = { current: T };

type UseTimelineCardSpacingArgs = {
  releaseCardRefs: MutableRef<Map<string, HTMLElement>>;
  developmentCardRefs: MutableRef<Map<string, HTMLElement>>;
  layoutKey: unknown;
  setMinGapOverride: (
    updater: (current: number | undefined) => number | undefined,
  ) => void;
  setEdgePaddingOverride: (
    updater: (current: number | undefined) => number | undefined,
  ) => void;
};

export function useTimelineCardSpacing({
  releaseCardRefs,
  developmentCardRefs,
  layoutKey,
  setMinGapOverride,
  setEdgePaddingOverride,
}: UseTimelineCardSpacingArgs) {
  // biome-ignore lint/correctness/useExhaustiveDependencies: layoutKey isn't read directly, but its identity must retrigger remeasurement.
  useLayoutEffect(() => {
    function measure() {
      const cards = [
        ...releaseCardRefs.current.values(),
        ...developmentCardRefs.current.values(),
      ];
      if (cards.length === 0) return;

      const measuredMax = Math.max(
        ...cards.map((el) => el.getBoundingClientRect().height),
      );
      const required = Math.ceil(measuredMax) + CARD_HEIGHT_BUFFER_PX;

      setMinGapOverride((current) => {
        const currentGap = current ?? DEFAULT_MIN_GAP_PX;
        return required > currentGap ? required : current;
      });

      setEdgePaddingOverride((current) => {
        const currentPadding = current ?? DEFAULT_EDGE_PADDING_PX;
        return required > currentPadding ? required : current;
      });
    }

    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, [
    developmentCardRefs,
    layoutKey,
    releaseCardRefs,
    setEdgePaddingOverride,
    setMinGapOverride,
  ]);
}

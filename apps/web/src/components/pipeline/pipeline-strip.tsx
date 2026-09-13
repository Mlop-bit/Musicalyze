"use client";

import { useRef } from "react";
import { PipelineDesktopTrack } from "./pipeline-desktop-track";
import { PipelineMobileList } from "./pipeline-mobile-list";
import { usePipelineScroll } from "./use-pipeline-scroll";

export function PipelineStrip() {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const trackRef = useRef<HTMLDivElement | null>(null);
  const mobileSectionRef = useRef<HTMLDivElement | null>(null);

  usePipelineScroll({ containerRef, trackRef, mobileSectionRef });

  return (
    <div id="how-it-works" className="border-t border-border bg-background">
      <PipelineDesktopTrack
        containerRef={(el) => (containerRef.current = el)}
        trackRef={(el) => (trackRef.current = el)}
      />
      <PipelineMobileList
        sectionRef={(el) => (mobileSectionRef.current = el)}
      />
    </div>
  );
}

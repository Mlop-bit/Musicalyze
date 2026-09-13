import { Fragment } from "react";
import { splitHeading } from "@/components/ui/split-heading";
import { HEADING_TEXT, STAGES } from "./pipeline-data";

type PipelineDesktopTrackProps = {
  containerRef: (el: HTMLDivElement | null) => void;
  trackRef: (el: HTMLDivElement | null) => void;
};

export function PipelineDesktopTrack({
  containerRef,
  trackRef,
}: PipelineDesktopTrackProps) {
  return (
    <div
      ref={containerRef}
      className="hidden lg:relative lg:block lg:h-screen lg:overflow-hidden"
    >
      <div className="absolute inset-0 z-10 flex items-center">
        <div ref={trackRef} className="relative flex items-center gap-20 px-10">
          <div className="w-[26vw] max-w-sm shrink-0">
            <span className="font-mono text-xs tracking-[0.15em] text-muted-foreground uppercase">
              How it works
            </span>
            <h2
              data-split-heading
              className="mt-4 text-4xl leading-[1.05] font-bold text-foreground xl:text-5xl"
            >
              {splitHeading(HEADING_TEXT)}
            </h2>
          </div>
          {STAGES.map((stage, index) => {
            const Icon = stage.icon;
            return (
              <Fragment key={stage.label}>
                <span
                  aria-hidden="true"
                  className="h-px w-16 shrink-0 bg-signal-violet/50 xl:w-24"
                />
                <div
                  data-stage-panel
                  data-active="false"
                  className="group relative flex w-[27vw] max-w-sm shrink-0 flex-col xl:w-[24vw]"
                >
                  <div className="flex items-start justify-between gap-4">
                    <span
                      data-stage-number
                      className="font-mono text-6xl font-bold text-border transition-colors duration-500 group-data-[active=true]:text-signal-violet/80 xl:text-7xl"
                    >
                      0{index + 1}
                    </span>
                    <Icon
                      aria-hidden="true"
                      className="mt-2 size-8 shrink-0 text-muted-foreground/50 transition-colors duration-500 group-data-[active=true]:text-signal-violet xl:size-9"
                    />
                  </div>
                  <p className="mt-5 text-2xl font-bold text-foreground xl:text-3xl">
                    {stage.label}
                  </p>
                  <p className="mt-3 text-sm text-muted-foreground xl:text-base">
                    {stage.detail}
                  </p>
                  <span className="mt-4 font-mono text-[0.65rem] tracking-[0.1em] text-muted-foreground/60 uppercase xl:text-xs">
                    {stage.meta}
                  </span>
                  <span
                    aria-hidden="true"
                    className="mt-6 block h-0.5 w-8 bg-border transition-[width,background-color] duration-500 group-data-[active=true]:w-16 group-data-[active=true]:bg-signal-violet"
                  />
                </div>
              </Fragment>
            );
          })}
          <div aria-hidden="true" className="w-[26vw] max-w-sm shrink-0" />
        </div>
      </div>
    </div>
  );
}

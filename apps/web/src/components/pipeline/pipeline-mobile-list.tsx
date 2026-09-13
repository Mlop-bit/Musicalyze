import { Fragment } from "react";
import { splitHeading } from "@/components/ui/split-heading";
import { HEADING_TEXT, STAGES } from "./pipeline-data";

type PipelineMobileListProps = {
  sectionRef: (el: HTMLDivElement | null) => void;
};

export function PipelineMobileList({ sectionRef }: PipelineMobileListProps) {
  return (
    <div
      ref={sectionRef}
      className="relative mx-auto w-full max-w-6xl overflow-hidden px-6 py-20 sm:px-10 sm:py-28 lg:hidden"
    >
      <div className="relative z-10">
        <h2
          data-split-heading
          className="max-w-2xl text-2xl font-bold text-foreground sm:text-3xl"
        >
          {splitHeading(HEADING_TEXT)}
        </h2>
        <div className="mt-16 flex flex-col items-stretch gap-2">
          {STAGES.map((stage, index) => {
            const Icon = stage.icon;
            return (
              <Fragment key={stage.label}>
                <div className="relative z-10 flex flex-col items-center gap-2.5 text-center">
                  <span className="flex size-9 shrink-0 items-center justify-center rounded-full border border-signal-violet bg-background">
                    <Icon
                      aria-hidden="true"
                      className="size-4 text-signal-violet"
                    />
                  </span>
                  <span className="font-mono text-[0.65rem] tracking-[0.15em] text-foreground uppercase sm:text-xs">
                    {stage.label}
                  </span>
                  <span className="text-xs text-muted-foreground sm:text-sm">
                    {stage.detail}
                  </span>
                  <span className="font-mono text-[0.6rem] tracking-[0.1em] text-muted-foreground/60 uppercase">
                    {stage.meta}
                  </span>
                </div>
                {index < STAGES.length - 1 && (
                  <div className="relative mx-auto h-8 w-px bg-border">
                    <div
                      data-connector-v
                      className="absolute inset-0 origin-top bg-signal-violet"
                    />
                  </div>
                )}
              </Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
}

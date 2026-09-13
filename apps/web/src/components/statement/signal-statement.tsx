"use client";

import { useRef } from "react";
import { splitHeading } from "@/components/ui/split-heading";
import { WaveFrame } from "@/components/ui/wave-frame";
import {
  AMBIENT_WAVE_PATHS,
  HEADING_TEXT,
  RAW_SIGNAL_PATH,
  SENTENCES,
} from "./signal-statement-data";
import { useSignalStatement } from "./use-signal-statement";

export function SignalStatement() {
  const sectionRef = useRef<HTMLDivElement | null>(null);
  const pathRef = useRef<SVGPathElement | null>(null);
  const linesRef = useRef<HTMLDivElement | null>(null);
  const headingRef = useRef<HTMLHeadingElement | null>(null);
  const waveRef = useRef<HTMLDivElement | null>(null);

  useSignalStatement({ sectionRef, pathRef, linesRef, headingRef, waveRef });

  return (
    <section
      ref={sectionRef}
      className="relative overflow-hidden border-t border-border"
    >
      <div
        className="pointer-events-none absolute inset-0 z-0"
        aria-hidden="true"
      >
        <div
          ref={waveRef}
          className="absolute inset-x-0 top-1/2 h-28 -translate-y-1/2 opacity-30"
        >
          <WaveFrame paths={AMBIENT_WAVE_PATHS} />
        </div>
      </div>

      <div className="relative z-10 mx-auto max-w-4xl px-6 py-24 sm:px-10 sm:py-32">
        <svg
          viewBox="0 0 150 60"
          className="h-8 w-32 text-signal-violet"
          aria-hidden="true"
        >
          <path
            ref={pathRef}
            d={RAW_SIGNAL_PATH}
            stroke="currentColor"
            strokeWidth={1.5}
            strokeLinecap="round"
            fill="none"
          />
        </svg>

        <h2
          ref={headingRef}
          data-split-heading
          className="mt-6 text-3xl leading-tight font-bold text-foreground sm:text-5xl"
        >
          {splitHeading(HEADING_TEXT)}
        </h2>

        <div ref={linesRef} className="mt-8 flex flex-col gap-2">
          {SENTENCES.map((sentence) => (
            <div key={sentence} className="overflow-hidden">
              <p
                data-statement-line
                className="text-2xl leading-snug font-medium text-foreground sm:text-4xl"
              >
                {sentence}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

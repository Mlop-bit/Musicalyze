"use client";

import gsap from "gsap";
import { useLayoutEffect, useRef } from "react";
import { prefersReducedMotion } from "@/lib/prefers-reduced-motion";
import { cn } from "@/lib/utils";
import {
  CLEAN_SIGNAL_PATH,
  NOISE_SIGNAL_VIEWBOX,
  NOISE_TO_SIGNAL_DOTS,
} from "./noise-signal-data";

type NoiseSignalBandProps = {
  className?: string;
};

export function NoiseSignalBand({ className }: NoiseSignalBandProps) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useLayoutEffect(() => {
    const svg = svgRef.current;
    if (!svg || prefersReducedMotion()) return;

    const ctx = gsap.context(() => {
      gsap.utils
        .toArray<SVGCircleElement>("[data-noise-dot]", svg)
        .forEach((dot) => {
          const chaos = Number(dot.dataset.chaos ?? 0);
          if (chaos < 0.03) return;
          const originalY = Number(dot.getAttribute("cy"));
          gsap.to(dot, {
            attr: {
              cy: () => originalY + (Math.random() - 0.5) * chaos * 16,
            },
            duration: 1.4 + Math.random() * 1.6,
            repeat: -1,
            repeatRefresh: true,
            ease: "sine.inOut",
          });
        });
    }, svg);

    return () => ctx.revert();
  }, []);

  return (
    <svg
      ref={svgRef}
      viewBox={NOISE_SIGNAL_VIEWBOX}
      preserveAspectRatio="none"
      className={cn("h-full w-full", className)}
      aria-hidden="true"
    >
      {NOISE_TO_SIGNAL_DOTS.map((dot) => (
        <circle
          key={`${dot.x}-${dot.y}`}
          data-noise-dot
          data-chaos={dot.chaos}
          cx={dot.x}
          cy={dot.y}
          r={dot.r}
          className="fill-muted-foreground/40"
        />
      ))}
      <path
        d={CLEAN_SIGNAL_PATH}
        className="fill-none stroke-signal-violet"
        strokeWidth={1.5}
        strokeLinecap="round"
      />
    </svg>
  );
}

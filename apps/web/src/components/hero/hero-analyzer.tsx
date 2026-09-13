"use client";

import gsap from "gsap";
import { AudioLines } from "lucide-react";
import {
  forwardRef,
  lazy,
  Suspense,
  useCallback,
  useImperativeHandle,
  useRef,
  useSyncExternalStore,
} from "react";

export interface HeroAnalyzerHandle {
  arc: SVGCircleElement | null;
  dial: SVGGElement | null;
}

const CENTER = 80;
const DIAL_RADIUS = 40;
const ARC_RADIUS = 67;
const TICK_COUNT = 24;

function round(value: number) {
  return Math.round(value * 1000) / 1000;
}

const TICKS = Array.from({ length: TICK_COUNT }, (_, i) => {
  const angle = (i * 360) / TICK_COUNT;
  const rad = (angle * Math.PI) / 180;
  const long = i % 6 === 0;
  const inner = long ? DIAL_RADIUS - 7 : DIAL_RADIUS - 4;
  return {
    angle,
    long,
    x1: round(CENTER + DIAL_RADIUS * Math.sin(rad)),
    y1: round(CENTER - DIAL_RADIUS * Math.cos(rad)),
    x2: round(CENTER + inner * Math.sin(rad)),
    y2: round(CENTER - inner * Math.cos(rad)),
  };
});

function supportsSignalRing() {
  if (typeof navigator === "undefined" || !("gpu" in navigator)) return false;
  return !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function noSignalRingSupport() {
  return false;
}

function subscribeToNothing() {
  return () => {};
}

const HeroGpuCanvas = lazy(() =>
  import("./hero-gpu-canvas").then((mod) => ({ default: mod.HeroGpuCanvas })),
);

export const HeroAnalyzer = forwardRef<HeroAnalyzerHandle>(
  function HeroAnalyzer(_props, ref) {
    const arcRef = useRef<SVGCircleElement | null>(null);
    const dialRef = useRef<SVGGElement | null>(null);
    const svgWrapperRef = useRef<HTMLDivElement | null>(null);
    const gpuWrapperRef = useRef<HTMLDivElement | null>(null);
    const tryGpu = useSyncExternalStore(
      subscribeToNothing,
      supportsSignalRing,
      noSignalRingSupport,
    );

    useImperativeHandle(
      ref,
      () => ({
        get arc() {
          return arcRef.current;
        },
        get dial() {
          return dialRef.current;
        },
      }),
      [],
    );

    const handleGpuReady = useCallback(() => {
      if (gpuWrapperRef.current) {
        gsap.to(gpuWrapperRef.current, {
          opacity: 1,
          duration: 1,
          ease: "power2.out",
        });
      }
      if (svgWrapperRef.current) {
        gsap.to(svgWrapperRef.current, {
          opacity: 0,
          duration: 1,
          ease: "power2.out",
        });
      }
    }, []);

    return (
      <div className="relative flex aspect-square h-full w-full shrink-0 items-center justify-center">
        {tryGpu && (
          <div
            ref={gpuWrapperRef}
            className="absolute inset-0 overflow-hidden opacity-0"
          >
            <Suspense fallback={null}>
              <HeroGpuCanvas onReady={handleGpuReady} />
            </Suspense>
          </div>
        )}
        <div ref={svgWrapperRef} className="absolute inset-0">
          <svg
            viewBox="0 0 160 160"
            className="absolute inset-0 h-full w-full"
            aria-hidden="true"
          >
            <circle
              cx={CENTER}
              cy={CENTER}
              r={76}
              className="fill-none stroke-border"
              strokeWidth={1}
            />
            <circle
              cx={CENTER}
              cy={CENTER}
              r={58}
              className="fill-none stroke-border"
              strokeWidth={1}
            />
            <g ref={dialRef} style={{ transformOrigin: "80px 80px" }}>
              {TICKS.map((tick) => (
                <line
                  key={tick.angle}
                  x1={tick.x1}
                  y1={tick.y1}
                  x2={tick.x2}
                  y2={tick.y2}
                  className="stroke-muted-foreground/50"
                  strokeWidth={tick.long ? 1.5 : 1}
                  strokeLinecap="round"
                />
              ))}
            </g>
            <circle
              ref={arcRef}
              cx={CENTER}
              cy={CENTER}
              r={ARC_RADIUS}
              className="fill-none stroke-signal-violet"
              strokeWidth={2}
              strokeLinecap="round"
              transform={`rotate(-90 ${CENTER} ${CENTER})`}
            />
          </svg>
        </div>
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="flex size-9 items-center justify-center rounded-full bg-background shadow-[0_0_0_1px_var(--color-border)]">
            <AudioLines
              aria-hidden="true"
              className="size-4 text-foreground/80"
            />
          </div>
        </div>
      </div>
    );
  },
);

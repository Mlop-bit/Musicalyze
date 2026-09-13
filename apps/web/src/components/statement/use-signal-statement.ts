import gsap from "gsap";
import { MorphSVGPlugin } from "gsap/MorphSVGPlugin";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLayoutEffect } from "react";
import {
  WAVE_DASH_DELTAS,
  WAVE_DURATIONS,
  WAVEFORM_PATH,
} from "./signal-statement-data";

gsap.registerPlugin(ScrollTrigger, MorphSVGPlugin);

type MutableRef<T> = { current: T };

type UseSignalStatementArgs = {
  sectionRef: MutableRef<HTMLDivElement | null>;
  pathRef: MutableRef<SVGPathElement | null>;
  linesRef: MutableRef<HTMLDivElement | null>;
  headingRef: MutableRef<HTMLHeadingElement | null>;
  waveRef: MutableRef<HTMLDivElement | null>;
};

export function useSignalStatement({
  sectionRef,
  pathRef,
  linesRef,
  headingRef,
  waveRef,
}: UseSignalStatementArgs) {
  useLayoutEffect(() => {
    const section = sectionRef.current;
    if (!section) return;

    const reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;

    const lines =
      linesRef.current?.querySelectorAll<HTMLElement>(
        "[data-statement-line]",
      ) ?? null;
    const headingChars =
      headingRef.current?.querySelectorAll<HTMLElement>(
        "[data-heading-char]",
      ) ?? null;
    const wavePaths =
      waveRef.current?.querySelectorAll<SVGPathElement>("[data-wave-path]") ??
      null;

    if (reduceMotion) {
      if (lines) gsap.set(lines, { yPercent: 0 });
      if (headingChars) gsap.set(headingChars, { yPercent: 0, opacity: 1 });
      if (wavePaths) gsap.set(wavePaths, { strokeDashoffset: 0 });
      return;
    }

    const ctx = gsap.context(() => {
      if (lines && lines.length > 0) {
        gsap.set(lines, { yPercent: 100 });
      }
      if (headingChars && headingChars.length > 0) {
        gsap.set(headingChars, { yPercent: 115, opacity: 0 });
      }

      const tl = gsap.timeline({
        scrollTrigger: { trigger: section, start: "top 70%", once: true },
      });

      if (headingChars && headingChars.length > 0) {
        tl.to(
          headingChars,
          {
            yPercent: 0,
            opacity: 1,
            duration: 0.5,
            ease: "power3.out",
            stagger: 0.025,
            onStart: () => gsap.set(headingChars, { willChange: "transform" }),
            onComplete: () => gsap.set(headingChars, { willChange: "auto" }),
          },
          0,
        );
      }

      if (pathRef.current) {
        tl.to(
          pathRef.current,
          { duration: 1.1, ease: "power2.inOut", morphSVG: WAVEFORM_PATH },
          0.2,
        );
      }

      if (lines && lines.length > 0) {
        tl.to(
          lines,
          { yPercent: 0, duration: 0.8, ease: "power3.out", stagger: 0.15 },
          pathRef.current ? "-=0.5" : 0.3,
        );
      }

      if (wavePaths && wavePaths.length > 0) {
        wavePaths.forEach((path, i) => {
          const delta = WAVE_DASH_DELTAS[i] ?? -160;
          const duration = WAVE_DURATIONS[i] ?? 12;
          gsap.to(path, {
            strokeDashoffset:
              delta >= 0 ? `+=${delta}` : `-=${Math.abs(delta)}`,
            duration,
            ease: "none",
            repeat: -1,
          });
        });
      }
    }, section);

    return () => ctx.revert();
  }, [headingRef, linesRef, pathRef, sectionRef, waveRef]);
}

import gsap from "gsap";
import { type RefObject, useLayoutEffect } from "react";
import { prefersReducedMotion } from "@/lib/prefers-reduced-motion";
import type { HeroAnalyzerHandle } from "./hero-analyzer";
import { getArcLength } from "./hero-motion";

type UseHeroIntroArgs = {
  sectionRef: RefObject<HTMLElement | null>;
  analyzerRef: RefObject<HeroAnalyzerHandle | null>;
  wordmarkRef: RefObject<HTMLHeadingElement | null>;
  taglineRef: RefObject<HTMLDivElement | null>;
  ctaRef: RefObject<HTMLDivElement | null>;
  noiseRef: RefObject<HTMLDivElement | null>;
  scrollCueRef: RefObject<HTMLButtonElement | null>;
};

export function useHeroIntro({
  sectionRef,
  analyzerRef,
  wordmarkRef,
  taglineRef,
  ctaRef,
  noiseRef,
  scrollCueRef,
}: UseHeroIntroArgs) {
  useLayoutEffect(() => {
    const reduceMotion = prefersReducedMotion();
    const arc = analyzerRef.current?.arc ?? null;
    const dial = analyzerRef.current?.dial ?? null;
    const wordmarkLetters =
      wordmarkRef.current?.querySelectorAll<HTMLElement>(
        "[data-wordmark-letter]",
      ) ?? null;

    if (reduceMotion) {
      if (arc) gsap.set(arc, { strokeDashoffset: 0 });
      if (wordmarkLetters)
        gsap.set(wordmarkLetters, { yPercent: 0, opacity: 1 });
      if (taglineRef.current)
        gsap.set(taglineRef.current, { autoAlpha: 1, y: 0 });
      if (ctaRef.current) gsap.set(ctaRef.current, { autoAlpha: 1, y: 0 });
      if (noiseRef.current) gsap.set(noiseRef.current, { autoAlpha: 1, y: 0 });
      if (scrollCueRef.current)
        gsap.set(scrollCueRef.current, { autoAlpha: 1, y: 0 });
      return;
    }

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

      if (arc) {
        const length = getArcLength(arc);
        gsap.set(arc, { strokeDasharray: length, strokeDashoffset: length });
        tl.to(
          arc,
          { strokeDashoffset: 0, duration: 1.1, ease: "power2.inOut" },
          0,
        );
      }

      if (wordmarkLetters && wordmarkLetters.length > 0) {
        gsap.set(wordmarkLetters, { yPercent: 130 });
        tl.to(
          wordmarkLetters,
          {
            yPercent: 0,
            duration: 0.9,
            ease: "expo.out",
            stagger: 0.02,
            onStart: () =>
              gsap.set(wordmarkLetters, { willChange: "transform" }),
            onComplete: () => gsap.set(wordmarkLetters, { willChange: "auto" }),
          },
          arc ? "-=0.7" : 0.1,
        );
      }

      if (taglineRef.current) {
        tl.fromTo(
          taglineRef.current,
          { autoAlpha: 0, y: 10 },
          { autoAlpha: 1, y: 0, duration: 0.6 },
          "-=0.4",
        );
      }

      if (ctaRef.current) {
        tl.fromTo(
          ctaRef.current,
          { autoAlpha: 0, y: 10 },
          { autoAlpha: 1, y: 0, duration: 0.5 },
          "-=0.3",
        );
      }

      if (noiseRef.current) {
        tl.fromTo(
          noiseRef.current,
          { autoAlpha: 0, y: 10 },
          { autoAlpha: 1, y: 0, duration: 0.6 },
          "-=0.2",
        );
      }

      if (scrollCueRef.current) {
        tl.fromTo(
          scrollCueRef.current,
          { autoAlpha: 0, y: 10 },
          { autoAlpha: 1, y: 0, duration: 0.6 },
          "-=0.2",
        );
      }

      if (dial) {
        gsap.to(dial, {
          rotation: 360,
          transformOrigin: "80px 80px",
          duration: 26,
          repeat: -1,
          ease: "none",
        });
      }
    }, sectionRef);

    return () => ctx.revert();
  }, [
    sectionRef,
    analyzerRef,
    wordmarkRef,
    taglineRef,
    ctaRef,
    noiseRef,
    scrollCueRef,
  ]);
}

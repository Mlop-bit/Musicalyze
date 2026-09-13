import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLayoutEffect } from "react";

gsap.registerPlugin(ScrollTrigger);

type MutableRef<T> = { current: T };

type UseTimelineScrollArgs = {
  releaseTrackRef: MutableRef<HTMLDivElement | null>;
  developmentTrackRef: MutableRef<HTMLDivElement | null>;
  releasePathRef: MutableRef<SVGPathElement | null>;
  developmentPathRef: MutableRef<SVGPathElement | null>;
  releaseCardRefs: MutableRef<Map<string, HTMLElement>>;
  developmentCardRefs: MutableRef<Map<string, HTMLElement>>;
  layoutKey: unknown;
};

export function useTimelineScroll({
  releaseTrackRef,
  developmentTrackRef,
  releasePathRef,
  developmentPathRef,
  releaseCardRefs,
  developmentCardRefs,
  layoutKey,
}: UseTimelineScrollArgs) {
  // biome-ignore lint/correctness/useExhaustiveDependencies: layoutKey isn't read directly, but its identity must retrigger the scroll setup.
  useLayoutEffect(() => {
    const reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;

    const rails = [
      { path: releasePathRef.current, trigger: releaseTrackRef.current },
      {
        path: developmentPathRef.current,
        trigger: developmentTrackRef.current,
      },
    ];

    const ctx = gsap.context(() => {
      for (const { path, trigger } of rails) {
        if (!path || !trigger) continue;
        const length = path.getTotalLength();

        if (reduceMotion) {
          gsap.set(path, {
            opacity: 1,
            strokeDasharray: length,
            strokeDashoffset: 0,
          });
          continue;
        }

        gsap.set(path, {
          opacity: 1,
          strokeDasharray: length,
          strokeDashoffset: length,
        });
        gsap.to(path, {
          strokeDashoffset: 0,
          ease: "none",
          scrollTrigger: {
            trigger,
            start: "top 75%",
            end: "bottom bottom",
            scrub: true,
          },
        });
      }

      for (const cards of [
        [...releaseCardRefs.current.values()],
        [...developmentCardRefs.current.values()],
      ]) {
        if (cards.length === 0) continue;

        if (reduceMotion) {
          gsap.set(cards, { opacity: 1, y: 0 });
          continue;
        }

        gsap.set(cards, { opacity: 0, y: 24 });
        ScrollTrigger.batch(cards, {
          start: "top 88%",
          once: true,
          onEnter: (batch) =>
            gsap.to(batch, {
              opacity: 1,
              y: 0,
              duration: 0.5,
              stagger: 0.08,
              ease: "power2.out",
            }),
        });
      }
    });

    return () => ctx.revert();
  }, [
    developmentCardRefs,
    developmentPathRef,
    developmentTrackRef,
    layoutKey,
    releaseCardRefs,
    releasePathRef,
    releaseTrackRef,
  ]);
}

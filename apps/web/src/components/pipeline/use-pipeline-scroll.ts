import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { useLayoutEffect } from "react";

gsap.registerPlugin(ScrollTrigger);

type MutableRef<T> = { current: T };

type UsePipelineScrollArgs = {
  containerRef: MutableRef<HTMLDivElement | null>;
  trackRef: MutableRef<HTMLDivElement | null>;
  mobileSectionRef: MutableRef<HTMLDivElement | null>;
};

function setupHeading(heading: HTMLElement | null, reduceMotion: boolean) {
  if (!heading) return;
  const chars = heading.querySelectorAll<HTMLElement>("[data-heading-char]");
  if (chars.length === 0) return;

  if (reduceMotion) {
    gsap.set(chars, { yPercent: 0, opacity: 1 });
    return;
  }

  gsap.set(chars, { yPercent: 115, opacity: 0 });
  gsap.to(chars, {
    yPercent: 0,
    opacity: 1,
    duration: 0.6,
    ease: "power3.out",
    stagger: 0.02,
    onStart: () => gsap.set(chars, { willChange: "transform" }),
    onComplete: () => gsap.set(chars, { willChange: "auto" }),
    scrollTrigger: { trigger: heading, start: "top 88%", once: true },
  });
}

export function usePipelineScroll({
  containerRef,
  trackRef,
  mobileSectionRef,
}: UsePipelineScrollArgs) {
  useLayoutEffect(() => {
    const mm = gsap.matchMedia();

    mm.add(
      {
        isDesktop: "(min-width: 1024px)",
        reduceMotion: "(prefers-reduced-motion: reduce)",
      },
      (context) => {
        const { isDesktop, reduceMotion } = context.conditions as {
          isDesktop: boolean;
          reduceMotion: boolean;
        };

        const track = trackRef.current;
        const container = containerRef.current;
        const mobileSection = mobileSectionRef.current;

        if (isDesktop && track && container) {
          setupHeading(
            container.querySelector<HTMLElement>("[data-split-heading]"),
            reduceMotion,
          );
        }

        if (isDesktop && track && container && !reduceMotion) {
          const panels = gsap.utils.toArray<HTMLElement>(
            "[data-stage-panel]",
            track,
          );
          const getDistance = () =>
            Math.max(track.scrollWidth - container.clientWidth, 0);
          gsap.set(track, { x: 0 });

          const tween = gsap.to(track, {
            x: () => -getDistance(),
            ease: "none",
            scrollTrigger: {
              trigger: container,
              start: "top top",
              end: () => `+=${getDistance()}`,
              scrub: 0.8,
              pin: true,
              invalidateOnRefresh: true,
              onEnter: () => gsap.set(track, { willChange: "transform" }),
              onEnterBack: () => gsap.set(track, { willChange: "transform" }),
              onLeave: () => gsap.set(track, { willChange: "auto" }),
              onLeaveBack: () => gsap.set(track, { willChange: "auto" }),
              onUpdate: () => {
                if (panels.length === 0) return;
                const containerRect = container.getBoundingClientRect();
                const containerCenter =
                  containerRect.left + containerRect.width / 2;
                let closestIndex = 0;
                let closestDistance = Infinity;

                panels.forEach((panel, i) => {
                  const rect = panel.getBoundingClientRect();
                  const panelCenter = rect.left + rect.width / 2;
                  const distanceFromCenter = Math.abs(
                    panelCenter - containerCenter,
                  );
                  if (distanceFromCenter < closestDistance) {
                    closestDistance = distanceFromCenter;
                    closestIndex = i;
                  }
                });

                panels.forEach((panel, i) => {
                  panel.setAttribute(
                    "data-active",
                    i === closestIndex ? "true" : "false",
                  );
                });
              },
            },
          });

          if (typeof document !== "undefined" && "fonts" in document) {
            document.fonts.ready.then(() => ScrollTrigger.refresh());
          }

          return () => {
            tween.scrollTrigger?.kill();
            tween.kill();
          };
        }

        if (track) {
          gsap.set(track, { clearProps: "transform" });
        }

        if (!isDesktop && mobileSection) {
          setupHeading(
            mobileSection.querySelector<HTMLElement>("[data-split-heading]"),
            reduceMotion,
          );

          const fills = gsap.utils.toArray<HTMLElement>(
            "[data-connector-v]",
            mobileSection,
          );

          if (reduceMotion) {
            gsap.set(fills, { scaleY: 1 });
            return;
          }

          gsap.set(fills, { scaleY: 0 });
          const tl = gsap.timeline({
            scrollTrigger: {
              trigger: mobileSection,
              start: "top 75%",
              end: "bottom 65%",
              scrub: 0.6,
            },
          });
          tl.to(fills, { scaleY: 1, ease: "none", stagger: 0.15 }, 0);

          return () => {
            tl.scrollTrigger?.kill();
            tl.kill();
          };
        }
      },
    );

    return () => mm.revert();
  }, [containerRef, mobileSectionRef, trackRef]);
}

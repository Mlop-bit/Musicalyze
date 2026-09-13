"use client";

import { ScrollSmoother } from "gsap/ScrollSmoother";
import { ChevronDown } from "lucide-react";
import Link from "next/link";
import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { TypingAnimation } from "@/components/ui/typing-animation";
import { authClient } from "@/lib/auth-client";
import { HeroAnalyzer, type HeroAnalyzerHandle } from "./hero-analyzer";
import { HeroWordmark } from "./hero-wordmark";
import { NoiseSignalBand } from "./noise-signal-band";
import { useHeroIntro } from "./use-hero-intro";

export const HERO_TAGLINE =
  "Tempo, key, energy, and mood - reconstructed where Spotify's API stopped.";

function signInWithSpotify() {
  authClient.signIn.social({ provider: "spotify", callbackURL: "/dashboard" });
}

function scrollToPipeline() {
  ScrollSmoother.get()?.scrollTo("#how-it-works", true, "top top");
}

function HeroCta() {
  const { data: session, isPending } = authClient.useSession();

  if (isPending) {
    return <div className="h-9 w-48" aria-hidden="true" />;
  }

  if (session) {
    return (
      <Link
        href="/dashboard"
        className="rounded-full bg-signal-violet px-6 py-2 text-sm font-semibold text-background transition-colors hover:bg-signal-violet/90"
      >
        Go to your dashboard
      </Link>
    );
  }

  return (
    <Button
      type="button"
      size="lg"
      onClick={signInWithSpotify}
      className="rounded-full bg-signal-violet px-6 text-background hover:bg-signal-violet/90"
    >
      Sign up with Spotify
    </Button>
  );
}

export function HeroSection() {
  const sectionRef = useRef<HTMLElement | null>(null);
  const analyzerRef = useRef<HeroAnalyzerHandle | null>(null);
  const wordmarkRef = useRef<HTMLHeadingElement | null>(null);
  const taglineRef = useRef<HTMLDivElement | null>(null);
  const ctaRef = useRef<HTMLDivElement | null>(null);
  const noiseRef = useRef<HTMLDivElement | null>(null);
  const scrollCueRef = useRef<HTMLButtonElement | null>(null);

  useHeroIntro({
    sectionRef,
    analyzerRef,
    wordmarkRef,
    taglineRef,
    ctaRef,
    noiseRef,
    scrollCueRef,
  });

  return (
    <section
      ref={sectionRef}
      className="relative flex min-h-[100svh] w-full flex-col overflow-hidden border-b border-border bg-background"
    >
      <div className="pointer-events-none absolute top-1/2 left-0 aspect-square w-[min(74vw,92vh)] max-w-[1300px] -translate-x-1/2 -translate-y-1/2">
        <HeroAnalyzer ref={analyzerRef} />
      </div>

      <div
        className="relative z-10 flex h-full flex-1 flex-col gap-6 py-16 pr-6 sm:pr-10 lg:pr-16"
        style={{
          paddingLeft: "max(1.5rem, calc(min(74vw,92vh) / 2 + 2rem))",
        }}
      >
        <div className="flex flex-1 flex-col justify-center gap-9">
          <div className="flex flex-col gap-7">
            <HeroWordmark ref={wordmarkRef} text="MUSICALYZE" />

            <div ref={taglineRef} className="flex min-w-0 items-start gap-4">
              <span
                className="mt-3 size-2 shrink-0 rounded-full bg-signal-violet"
                aria-hidden="true"
              />
              <TypingAnimation
                as="p"
                className="min-w-0 truncate font-sans text-lg leading-snug font-medium text-foreground/85 sm:text-xl"
              >
                {HERO_TAGLINE}
              </TypingAnimation>
            </div>

            <div ref={ctaRef}>
              <HeroCta />
            </div>
          </div>

          <div ref={noiseRef} className="flex flex-col gap-3">
            <span className="font-mono text-xs tracking-widest text-muted-foreground uppercase">
              Noise becomes signal
            </span>
            <div className="-mr-6 h-28 w-[calc(100%+1.5rem)] sm:-mr-10 sm:w-[calc(100%+2.5rem)] lg:-mr-16 lg:w-[calc(100%+4rem)]">
              <NoiseSignalBand className="opacity-80" />
            </div>
          </div>
        </div>

        <button
          ref={scrollCueRef}
          type="button"
          onClick={scrollToPipeline}
          className="mt-auto flex w-fit items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          See how it works
          <ChevronDown aria-hidden="true" className="size-4" />
        </button>
      </div>
    </section>
  );
}

"use client";

import { cn } from "cn";
import { ArrowDown } from "lucide-react";
import Link from "next/link";
import BlurText from "@/components/react-bits/BlurText";
import CountUp from "@/components/react-bits/CountUp";
import { Turntable } from "@/components/spotify/turntable";
import { buttonVariants } from "@/components/ui/button-variants";

function FloatChip({
  className,
  children,
}: {
  className: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className={`surface float absolute rounded-2xl px-4 py-3 backdrop-blur-xl [animation:float_7s_ease-in-out_infinite] ${className}`}
    >
      {children}
    </div>
  );
}

export function LandingHero() {
  return (
    <section className="relative flex min-h-dvh items-center overflow-hidden px-6 pb-16 pt-32 lg:px-14">
      <div className="grid w-full items-center gap-6 lg:grid-cols-[1fr_1.1fr]">
        <div>
          <h1 className="text-5xl font-semibold leading-[0.95] tracking-tight sm:text-7xl">
            <BlurText
              text="Your playlists, ordered by"
              animateBy="words"
              delay={70}
            />
            <span className="mt-1 block font-script text-7xl font-normal leading-[0.9] text-brand sm:text-[9rem]">
              mood.
            </span>
          </h1>
          <p className="pane mt-6 max-w-lg rounded-3xl p-5 text-lg text-foreground/80">
            Spotify closed its audio-analysis API. Musicalyze listens to every
            track again with an open audio model, then orders your music by how
            it actually sounds.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link
              href="/login"
              className={cn(
                buttonVariants({ size: "lg" }),
                "px-6 font-semibold shadow-lg shadow-brand/30",
              )}
            >
              Continue with Spotify
            </Link>
            <a
              href="#how"
              className="press glass-clear inline-flex h-10 items-center gap-2 rounded-full px-5 text-sm font-medium"
            >
              How it works
              <ArrowDown className="size-4" />
            </a>
          </div>
        </div>

        <div className="relative h-[24rem] sm:h-[34rem]">
          <Turntable image={null} active busy={false} />
          <FloatChip className="left-0 top-6">
            <p className="text-2xl font-semibold tabular-nums">
              <CountUp to={56} duration={1.6} />
            </p>
            <p className="text-xs text-muted-foreground">mood and theme tags</p>
          </FloatChip>
          <FloatChip className="bottom-10 right-0 [animation-delay:-3s]">
            <p className="text-2xl font-semibold tabular-nums">
              <CountUp to={30} duration={1.6} /> s
            </p>
            <p className="text-xs text-muted-foreground">
              preview listened per track
            </p>
          </FloatChip>
        </div>
      </div>
    </section>
  );
}

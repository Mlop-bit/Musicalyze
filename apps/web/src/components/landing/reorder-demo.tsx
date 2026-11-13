"use client";

import { LayoutGroup, m } from "motion/react";
import { useEffect, useState } from "react";
import { moodColor } from "@/lib/mood-color";

type DemoTrack = { id: string; title: string; artist: string; mood: number };

const TRACKS: DemoTrack[] = [
  { id: "a", title: "Slow Orbit", artist: "Halden", mood: 0.04 },
  { id: "b", title: "Glass Harbour", artist: "Mira Voss", mood: 0.16 },
  { id: "c", title: "Late Trains", artist: "North Plate", mood: 0.28 },
  { id: "d", title: "Paper Sun", artist: "Ilo", mood: 0.42 },
  { id: "e", title: "Neon Laundry", artist: "Casa Verde", mood: 0.58 },
  { id: "f", title: "Fast Lanes", artist: "The Quiet Few", mood: 0.72 },
  { id: "g", title: "Overdrive Sunday", artist: "Kesh", mood: 0.86 },
  { id: "h", title: "Open Roof", artist: "Tamsin", mood: 0.97 },
];

const SHUFFLED = ["e", "a", "h", "c", "g", "b", "f", "d"];
const CYCLE_MS = 3400;

const byId = new Map(TRACKS.map((track) => [track.id, track]));

export function ReorderDemo() {
  const [ordered, setOrdered] = useState(false);

  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setOrdered(true);
      return;
    }
    const timer = setInterval(
      () => setOrdered((current) => !current),
      CYCLE_MS,
    );
    return () => clearInterval(timer);
  }, []);

  const rows = (ordered ? TRACKS.map((track) => track.id) : SHUFFLED).flatMap(
    (id) => byId.get(id) ?? [],
  );

  return (
    <div className="surface rounded-3xl p-3 backdrop-blur-xl sm:p-4">
      <div className="mb-3 flex items-center justify-between px-2 text-sm">
        <span className="font-medium">Example playlist</span>
        <m.span
          key={String(ordered)}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-full bg-brand px-3 py-0.5 text-xs font-semibold text-brand-foreground"
        >
          {ordered ? "Ordered by mood" : "Shuffled"}
        </m.span>
      </div>
      <LayoutGroup>
        <ul className="space-y-1.5">
          {rows.map((track, index) => (
            <m.li
              key={track.id}
              layout
              transition={{
                type: "spring",
                stiffness: 260,
                damping: 28,
                mass: 0.9,
              }}
              className="glass-clear flex items-center gap-3 rounded-2xl px-3 py-2"
            >
              <span className="w-5 text-right text-xs tabular-nums text-muted-foreground">
                {index + 1}
              </span>
              <span
                className="size-8 shrink-0 rounded-full"
                style={{ background: moodColor(track.mood) }}
              />
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-medium">
                  {track.title}
                </span>
                <span className="block truncate text-xs text-muted-foreground">
                  {track.artist}
                </span>
              </span>
              <span className="hidden h-1.5 w-24 overflow-hidden rounded-full bg-foreground/10 sm:block">
                <span
                  className="block h-full rounded-full"
                  style={{
                    width: `${track.mood * 100}%`,
                    background: moodColor(track.mood),
                  }}
                />
              </span>
            </m.li>
          ))}
        </ul>
      </LayoutGroup>
      <p className="mt-3 px-2 text-xs text-muted-foreground">
        Synthetic example tracks, to show the idea.
      </p>
    </div>
  );
}

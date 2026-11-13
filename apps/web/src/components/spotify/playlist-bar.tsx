"use client";

import BlurText from "@/components/react-bits/BlurText";
import type { playlistStats } from "@/lib/playlist-stats";
import type { Playlist } from "@/server/spotify/schema";
import { BarStats } from "./bar-stats";
import { OrderControls } from "./order-controls";
import { OrderProgress } from "./order-progress";
import { orderStatus } from "./order-status";
import { Turntable } from "./turntable";
import type { MoodOrder } from "./use-mood-order";

type Props = {
  playlist: Playlist | null;
  mood: MoodOrder;
  stats: ReturnType<typeof playlistStats>;
  trackCount: number;
};

export function PlaylistBar({ playlist, mood, stats, trackCount }: Props) {
  const status = playlist ? orderStatus(playlist, mood) : null;

  return (
    <div className="surface relative flex h-28 items-center gap-5 overflow-hidden rounded-3xl pr-4 text-foreground">
      <div
        aria-hidden="true"
        className="absolute -left-10 top-1/2 size-56 -translate-y-1/2 rounded-full bg-brand/25 blur-[70px]"
      />
      <div className="relative h-full w-44 shrink-0">
        <Turntable
          image={playlist?.image ?? null}
          active={playlist !== null}
          busy={mood.running}
        />
      </div>
      {playlist && status ? (
        <>
          <div className="relative min-w-0 flex-1">
            <h2 className="truncate font-script text-4xl leading-[1.1] tracking-wide">
              <BlurText
                key={playlist.id}
                text={playlist.name}
                animateBy="words"
                delay={60}
              />
            </h2>
            <p
              className={`truncate text-xs ${status.isError ? "text-destructive" : "text-muted-foreground"}`}
            >
              {status.text}
            </p>
          </div>
          {trackCount > 0 && <BarStats stats={stats} />}
          <div className="relative">
            <OrderControls
              playlist={playlist}
              mood={mood}
              trackCount={trackCount}
            />
          </div>
          {mood.running && (
            <OrderProgress
              done={mood.progress?.done ?? 0}
              total={mood.progress?.total ?? 0}
            />
          )}
        </>
      ) : (
        <p className="relative font-script text-4xl leading-none">
          Pick a record
        </p>
      )}
    </div>
  );
}

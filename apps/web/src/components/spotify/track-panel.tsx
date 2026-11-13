"use client";

import { useQuery } from "@tanstack/react-query";
import { playlistStats } from "@/lib/playlist-stats";
import type { Playlist } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";
import { PlaylistBar } from "./playlist-bar";
import { TrackError } from "./track-error";
import { TrackRows } from "./track-rows";
import { useMoodOrder } from "./use-mood-order";

function ListHeader() {
  return (
    <div className="flex shrink-0 items-center gap-3 border-b border-border px-4 py-2 text-xs text-muted-foreground">
      <span className="w-7 text-right">#</span>
      <span className="flex-1">Title</span>
      <span className="hidden w-48 md:block">Album</span>
      <span className="w-10 text-right">Time</span>
    </div>
  );
}

export function TrackPanel({ playlist }: { playlist: Playlist | null }) {
  const trpc = useTRPC();
  const tracksQuery = useQuery(
    trpc.spotify.playlistTracks.queryOptions(
      { playlistId: playlist?.id ?? "" },
      { enabled: playlist !== null },
    ),
  );
  const tracks = tracksQuery.data ?? [];
  const mood = useMoodOrder(tracks);

  return (
    <section className="grid h-full min-h-0 grid-rows-[auto_minmax(0,1fr)] gap-3">
      <PlaylistBar
        playlist={playlist}
        mood={mood}
        stats={playlistStats(tracks)}
        trackCount={tracks.length}
      />
      <div className="surface flex min-h-0 flex-col overflow-hidden rounded-3xl">
        <ListHeader />
        <div className="min-h-0 flex-1 overflow-y-auto p-1.5">
          {playlist === null ? null : tracksQuery.isPending ? (
            <p className="p-4 text-sm text-muted-foreground">Loading tracks…</p>
          ) : tracksQuery.error ? (
            <TrackError message={tracksQuery.error.message} />
          ) : tracks.length === 0 ? (
            <p className="p-4 text-sm text-muted-foreground">
              This playlist is empty.
            </p>
          ) : (
            <TrackRows tracks={mood.ordered} details={mood.details} />
          )}
        </div>
      </div>
    </section>
  );
}

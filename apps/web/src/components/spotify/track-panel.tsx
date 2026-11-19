"use client";

import { useQuery } from "@tanstack/react-query";
import { playlistStats } from "@/lib/playlist-stats";
import type { Playlist } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";
import { PlaylistBar } from "./playlist-bar";
import { TracksBody } from "./tracks-body";
import { useMoodOrder } from "./use-mood-order";
import { useRecommend } from "./use-recommend";

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

export type AdoptedJob = { jobId: string; kind: "reorder" | "recommend" };

type Props = { playlist: Playlist | null; adopt?: AdoptedJob };

export function TrackPanel({ playlist, adopt }: Props) {
  const trpc = useTRPC();
  const tracksQuery = useQuery(
    trpc.spotify.playlistTracks.queryOptions(
      { playlistId: playlist?.id ?? "" },
      { enabled: playlist !== null },
    ),
  );
  const tracks = tracksQuery.data ?? [];
  const mood = useMoodOrder(
    tracks,
    playlist,
    adopt?.kind === "reorder" ? adopt.jobId : undefined,
  );
  const similar = useRecommend(
    playlist,
    adopt?.kind === "recommend" ? adopt.jobId : undefined,
  );

  return (
    <section className="grid h-full min-h-0 grid-rows-[auto_minmax(0,1fr)] gap-3">
      <PlaylistBar
        playlist={playlist}
        mood={mood}
        similar={similar}
        stats={playlistStats(tracks)}
        trackCount={tracks.length}
      />
      <div className="surface flex min-h-0 flex-col overflow-hidden rounded-3xl">
        <ListHeader />
        <div className="min-h-0 flex-1 overflow-y-auto p-1.5">
          {playlist === null ? null : (
            <TracksBody query={tracksQuery} mood={mood} similar={similar} />
          )}
        </div>
      </div>
    </section>
  );
}

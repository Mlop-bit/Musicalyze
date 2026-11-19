"use client";

import { useQuery } from "@tanstack/react-query";
import type { Playlist } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";
import { ExpandedActions } from "./expanded-actions";
import { similarStatus } from "./similar-status";
import { TracksBody } from "./tracks-body";
import { useMoodOrder } from "./use-mood-order";
import { useRecommend } from "./use-recommend";

export function ExpandedPlaylist({ playlist }: { playlist: Playlist }) {
  const trpc = useTRPC();
  const query = useQuery(
    trpc.spotify.playlistTracks.queryOptions({ playlistId: playlist.id }),
  );
  const mood = useMoodOrder(query.data ?? [], playlist);
  const similar = useRecommend(playlist);
  const status = similar.active ? similarStatus(similar) : null;
  const message =
    status ?? (mood.error ? { text: mood.error, isError: true } : null);

  return (
    <div className="border-t border-border px-4 py-3">
      <div className="max-h-80 overflow-y-auto">
        <TracksBody query={query} mood={mood} similar={similar} compact />
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <ExpandedActions playlist={playlist} mood={mood} similar={similar} />
        {message && (
          <span
            role={message.isError ? "alert" : undefined}
            className={`text-xs ${message.isError ? "text-destructive" : "text-muted-foreground"}`}
          >
            {message.text}
          </span>
        )}
      </div>
    </div>
  );
}

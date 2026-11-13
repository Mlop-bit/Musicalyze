"use client";

import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import type { Playlist } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";
import { ModeSelect } from "./mode-select";
import { OrderDecision } from "./order-decision";
import { TrackError } from "./track-error";
import { TrackRows } from "./track-rows";
import { useMoodOrder } from "./use-mood-order";

export function ExpandedPlaylist({ playlist }: { playlist: Playlist }) {
  const trpc = useTRPC();
  const tracksQuery = useQuery(
    trpc.spotify.playlistTracks.queryOptions({ playlistId: playlist.id }),
  );
  const mood = useMoodOrder(tracksQuery.data ?? []);

  return (
    <div className="border-t border-border px-4 py-3">
      {tracksQuery.isPending ? (
        <p className="py-3 text-sm text-muted-foreground">Loading tracks…</p>
      ) : tracksQuery.error ? (
        <TrackError message={tracksQuery.error.message} />
      ) : mood.ordered.length === 0 ? (
        <p className="py-3 text-sm text-muted-foreground">
          This playlist is empty.
        </p>
      ) : (
        <div className="max-h-80 overflow-y-auto">
          <TrackRows tracks={mood.ordered} details={mood.details} compact />
        </div>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {mood.isOrdered ? (
          <OrderDecision
            playlist={playlist}
            ordered={mood.ordered}
            onDone={mood.reset}
          />
        ) : (
          <>
            <ModeSelect
              value={mood.mode}
              onValueChange={mood.setMode}
              disabled={mood.running}
            />
            <Button
              type="button"
              size="sm"
              disabled={mood.running || mood.ordered.length < 2}
              onClick={mood.run}
            >
              {mood.running ? "Ordering…" : "Order by mood"}
            </Button>
          </>
        )}
        {mood.error && (
          <span role="alert" className="text-xs text-destructive">
            {mood.error}
          </span>
        )}
      </div>
    </div>
  );
}

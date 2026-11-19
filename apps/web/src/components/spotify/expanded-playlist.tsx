"use client";

import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import type { Playlist } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";
import { FindSimilarButton } from "./find-similar-button";
import { ModeSelect } from "./mode-select";
import { OrderDecision } from "./order-decision";
import { SimilarControls } from "./similar-controls";
import { SimilarList } from "./similar-list";
import { similarStatus } from "./similar-status";
import { TrackError } from "./track-error";
import { TrackRows } from "./track-rows";
import { useMoodOrder } from "./use-mood-order";
import { useRecommend } from "./use-recommend";

export function ExpandedPlaylist({ playlist }: { playlist: Playlist }) {
  const trpc = useTRPC();
  const tracksQuery = useQuery(
    trpc.spotify.playlistTracks.queryOptions({ playlistId: playlist.id }),
  );
  const mood = useMoodOrder(tracksQuery.data ?? [], playlist);
  const similar = useRecommend(playlist);
  const status = similar.active ? similarStatus(similar) : null;

  return (
    <div className="border-t border-border px-4 py-3">
      {similar.active ? (
        <div className="max-h-80 overflow-y-auto">
          <SimilarList similar={similar} />
        </div>
      ) : tracksQuery.isPending ? (
        <p className="py-3 text-sm text-muted-foreground">Loading tracks…</p>
      ) : tracksQuery.error ? (
        <TrackError message={tracksQuery.error.message} />
      ) : mood.ordered.length === 0 ? (
        <p className="py-3 text-sm text-muted-foreground">
          This playlist is empty.
        </p>
      ) : (
        <div className="max-h-80 overflow-y-auto">
          <TrackRows
            tracks={mood.ordered}
            details={mood.details}
            onFindSimilar={(track) =>
              similar.run(track.id ?? undefined, track.name)
            }
            compact
          />
        </div>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {similar.active ? (
          <SimilarControls playlist={playlist} similar={similar} size="sm" />
        ) : mood.isOrdered ? (
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
            <FindSimilarButton
              size="sm"
              onClick={() => similar.run()}
              disabled={mood.running || mood.ordered.length === 0}
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
        {status && (
          <span
            role={status.isError ? "alert" : undefined}
            className={`text-xs ${status.isError ? "text-destructive" : "text-muted-foreground"}`}
          >
            {status.text}
          </span>
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

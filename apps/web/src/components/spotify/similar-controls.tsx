"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Tip } from "@/components/ui/tip";
import { LIKED_ID, type Playlist } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";
import type { Recommend } from "./use-recommend";

type Props = {
  playlist: Playlist;
  similar: Recommend;
  size?: "sm" | "lg";
};

export function SimilarControls({ playlist, similar, size = "lg" }: Props) {
  const trpc = useTRPC();
  const queryClient = useQueryClient();
  const add = useMutation(
    trpc.recommend.addToPlaylist.mutationOptions({
      onSuccess: async () => {
        await queryClient.invalidateQueries(
          trpc.spotify.playlistTracks.queryFilter({ playlistId: playlist.id }),
        );
        similar.reset();
      },
    }),
  );
  const addable = similar.tracks.flatMap((track) =>
    track.id && !track.id.startsWith("deezer:") ? [track.id] : [],
  );
  const canAdd = playlist.id !== LIKED_ID && addable.length > 0;

  return (
    <div className="flex items-center gap-2">
      {canAdd && (
        <Tip label="Adds these tracks to the end of this playlist on Spotify.">
          <Button
            type="button"
            size={size}
            disabled={add.isPending}
            onClick={() =>
              add.mutate({
                playlistId: playlist.id,
                trackIds: addable,
              })
            }
            className={
              size === "lg"
                ? "h-12 px-6 font-semibold shadow-xl shadow-brand/40"
                : "font-semibold"
            }
          >
            {add.isPending ? "Adding…" : `Add ${addable.length} to playlist`}
          </Button>
        </Tip>
      )}
      <Tip label="Closes the results without changing anything.">
        <Button
          type="button"
          variant="outline"
          size={size}
          disabled={add.isPending || similar.running}
          onClick={similar.reset}
          className={size === "lg" ? "h-12" : ""}
        >
          Dismiss
        </Button>
      </Tip>
      {add.error && (
        <span role="alert" className="max-w-56 text-xs text-destructive">
          {add.error.message}
        </span>
      )}
    </div>
  );
}

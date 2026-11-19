"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
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
  const canAdd = playlist.id !== LIKED_ID && similar.tracks.length > 0;

  return (
    <div className="flex items-center gap-2">
      {canAdd && (
        <Button
          type="button"
          size={size}
          disabled={add.isPending}
          onClick={() =>
            add.mutate({
              playlistId: playlist.id,
              trackIds: similar.tracks.flatMap((track) => track.id ?? []),
            })
          }
          className={
            size === "lg"
              ? "h-12 px-6 font-semibold shadow-xl shadow-brand/40"
              : "font-semibold"
          }
        >
          {add.isPending
            ? "Adding…"
            : `Add ${similar.tracks.length} to playlist`}
        </Button>
      )}
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
      {add.error && (
        <span role="alert" className="max-w-56 text-xs text-destructive">
          {add.error.message}
        </span>
      )}
    </div>
  );
}

"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Tip } from "@/components/ui/tip";
import {
  LIKED_ID,
  type Playlist,
  type PlaylistTrack,
} from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";

type Props = {
  playlist: Playlist;
  ordered: PlaylistTrack[];
  onDone: () => void;
  size?: "sm" | "lg";
  className?: string;
};

export function OrderDecision({
  playlist,
  ordered,
  onDone,
  size = "sm",
  className,
}: Props) {
  const trpc = useTRPC();
  const queryClient = useQueryClient();
  const save = useMutation(
    trpc.spotify.saveOrder.mutationOptions({
      onSuccess: async () => {
        await queryClient.invalidateQueries(
          trpc.spotify.playlistTracks.queryFilter({ playlistId: playlist.id }),
        );
        onDone();
      },
    }),
  );
  const canSave = playlist.id !== LIKED_ID;

  return (
    <div className={className}>
      <div className="flex items-center gap-2">
        {canSave && (
          <Tip label="Writes this order to the playlist on Spotify.">
            <Button
              type="button"
              size={size}
              disabled={save.isPending}
              onClick={() =>
                save.mutate({
                  playlistId: playlist.id,
                  trackIds: ordered.flatMap((track) => track.id ?? []),
                })
              }
              className="font-semibold"
            >
              {save.isPending ? "Saving…" : "Save to Spotify"}
            </Button>
          </Tip>
        )}
        <Tip label="Throws the new order away and keeps the playlist as it is.">
          <Button
            type="button"
            variant="outline"
            size={size}
            disabled={save.isPending}
            onClick={onDone}
          >
            Discard
          </Button>
        </Tip>
      </div>
      {save.error && (
        <p role="alert" className="mt-1 text-xs text-destructive">
          {save.error.message}
        </p>
      )}
    </div>
  );
}

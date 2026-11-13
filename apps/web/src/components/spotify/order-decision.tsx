"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
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
        )}
        <Button
          type="button"
          variant="outline"
          size={size}
          disabled={save.isPending}
          onClick={onDone}
        >
          Discard
        </Button>
      </div>
      {save.error && (
        <p role="alert" className="mt-1 text-xs text-destructive">
          {save.error.message}
        </p>
      )}
    </div>
  );
}

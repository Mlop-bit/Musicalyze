import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import type { Playlist } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";
import { useRecommendJob } from "./use-recommend-job";

export function useRecommend(
  playlist: Pick<Playlist, "id" | "name"> | null,
  adoptedJobId?: string,
) {
  const trpc = useTRPC();
  const [label, setLabel] = useState<string | null>(null);
  const [adopted, setAdopted] = useState(adoptedJobId);
  const start = useMutation(trpc.recommend.start.mutationOptions());
  const jobId = start.data?.jobId ?? adopted;

  return {
    ...useRecommendJob(start, label, jobId, () => setAdopted(undefined)),
    run: (
      trackId?: string,
      trackName?: string,
      source: "library" | "discover" = "library",
    ) => {
      if (!playlist) return;
      setLabel(trackName ?? null);
      start.mutate({
        playlistId: playlist.id,
        trackId,
        title: trackName ?? playlist.name,
        source,
        limit: 20,
      });
    },
  };
}

export type Recommend = ReturnType<typeof useRecommend>;

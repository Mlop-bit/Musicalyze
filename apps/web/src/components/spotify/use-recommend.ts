import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useTRPC } from "@/trpc/client";
import { useRecommendJob } from "./use-recommend-job";

export function useRecommend(playlistId: string | undefined) {
  const trpc = useTRPC();
  const [label, setLabel] = useState<string | null>(null);
  const start = useMutation(trpc.recommend.start.mutationOptions());

  return {
    ...useRecommendJob(start, label),
    run: (trackId?: string, trackName?: string) => {
      if (!playlistId) return;
      setLabel(trackName ?? null);
      start.mutate({ playlistId, trackId, limit: 20 });
    },
  };
}

export type Recommend = ReturnType<typeof useRecommend>;

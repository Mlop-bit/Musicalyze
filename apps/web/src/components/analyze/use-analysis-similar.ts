import { useMutation } from "@tanstack/react-query";
import { useRecommendJob } from "@/components/spotify/use-recommend-job";
import { useTRPC } from "@/trpc/client";

export function useAnalysisSimilar(trackId: string, title: string) {
  const trpc = useTRPC();
  const start = useMutation(trpc.recommend.similarToAnalysis.mutationOptions());

  return {
    ...useRecommendJob(start, title, start.data?.jobId, () => undefined),
    run: () => start.mutate({ trackId, title, limit: 20 }),
  };
}

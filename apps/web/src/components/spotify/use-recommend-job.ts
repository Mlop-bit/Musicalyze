import { useQuery } from "@tanstack/react-query";
import { useTRPC } from "@/trpc/client";

const POLL_MS = 1500;

type Start = {
  isPending: boolean;
  isError: boolean;
  error: { message: string } | null;
  data: { jobId: string; candidates: number } | undefined;
  reset: () => void;
};

export function useRecommendJob(start: Start, label: string | null) {
  const trpc = useTRPC();
  const jobId = start.data?.jobId;
  const job = useQuery(
    trpc.recommend.job.queryOptions(
      { jobId: jobId ?? "" },
      {
        enabled: jobId !== undefined,
        refetchInterval: (query) =>
          query.state.data?.status === "succeeded" ||
          query.state.data?.status === "failed"
            ? false
            : POLL_MS,
      },
    ),
  );
  const finished = job.data?.status === "succeeded";
  const failed = job.data?.status === "failed";

  return {
    active: start.isPending || jobId !== undefined || start.isError,
    running: start.isPending || (jobId !== undefined && !finished && !failed),
    finished,
    tracks: finished ? (job.data?.tracks ?? []) : [],
    dropped: job.data?.dropped ?? 0,
    candidates: start.data?.candidates ?? 0,
    progress: job.data
      ? { done: job.data.done, total: job.data.total, phase: job.data.phase }
      : null,
    error:
      start.error?.message ?? job.error?.message ?? job.data?.error ?? null,
    label,
    reset: start.reset,
  };
}

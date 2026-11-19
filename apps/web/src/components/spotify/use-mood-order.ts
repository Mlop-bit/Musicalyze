import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { sortByOrder } from "@/lib/playlist-stats";
import type { ReorderMode } from "@/lib/reorder-modes";
import { toDescriptors } from "@/lib/track-descriptors";
import type { PlaylistTrack } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";

const POLL_MS = 1500;

export function useMoodOrder(tracks: PlaylistTrack[]) {
  const trpc = useTRPC();
  const [mode, setMode] = useState<ReorderMode>("similarity");
  const start = useMutation(trpc.mood.reorder.mutationOptions());
  const jobId = start.data?.jobId;
  const job = useQuery(
    trpc.mood.job.queryOptions(
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

  const order =
    job.data?.status === "succeeded" ? job.data.result?.order : undefined;
  const ordered = useMemo(
    () => (order ? sortByOrder(tracks, order) : tracks),
    [tracks, order],
  );
  const running =
    start.isPending ||
    (jobId !== undefined && !order && job.data?.status !== "failed");
  const error =
    start.error?.message ?? job.error?.message ?? job.data?.error ?? null;

  function run() {
    start.mutate({ tracks: toDescriptors(tracks), mode });
  }

  const details = useMemo(
    () =>
      new Map(
        (job.data?.result?.details ?? []).map((detail) => [
          detail.track_id,
          detail,
        ]),
      ),
    [job.data?.result?.details],
  );

  return {
    mode,
    setMode,
    details,
    ordered,
    isOrdered: order !== undefined,
    running,
    error,
    skipped: job.data?.result?.skipped.length ?? 0,
    progress: job.data
      ? { done: job.data.done, total: job.data.total, phase: job.data.phase }
      : null,
    run,
    reset: start.reset,
  };
}

export type MoodOrder = ReturnType<typeof useMoodOrder>;

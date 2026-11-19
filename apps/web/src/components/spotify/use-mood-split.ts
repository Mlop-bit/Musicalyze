import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { toDescriptors } from "@/lib/track-descriptors";
import type { Playlist, PlaylistTrack } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";

const POLL_MS = 1500;
export const MIN_TRACKS_FOR_SPLIT = 6;

export interface ResolvedCluster {
  name: string;
  tracks: PlaylistTrack[];
}

export function useMoodSplit(
  tracks: PlaylistTrack[],
  playlist: Pick<Playlist, "id" | "name"> | null,
  adoptedJobId?: string,
) {
  const trpc = useTRPC();
  const [k, setK] = useState<number | undefined>(undefined);
  const start = useMutation(trpc.mood.split.mutationOptions());
  const [adopted, setAdopted] = useState(adoptedJobId);
  const jobId = start.data?.jobId ?? adopted;

  const job = useQuery(
    trpc.mood.splitJob.queryOptions(
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

  const rawClusters =
    job.data?.status === "succeeded" ? job.data.result?.clusters : undefined;

  const clusters = useMemo<ResolvedCluster[] | null>(() => {
    if (!rawClusters) return null;
    const byId = new Map(tracks.map((track) => [track.id, track]));
    return rawClusters.map((cluster) => ({
      name: cluster.name,
      tracks: cluster.track_ids
        .map((id) => byId.get(id))
        .filter((track): track is PlaylistTrack => track !== undefined),
    }));
  }, [rawClusters, tracks]);

  const canSplit = tracks.length >= MIN_TRACKS_FOR_SPLIT;
  const running =
    start.isPending ||
    (jobId !== undefined && !rawClusters && job.data?.status !== "failed");
  const error =
    start.error?.message ?? job.error?.message ?? job.data?.error ?? null;

  function run() {
    if (!playlist || !canSplit) return;
    start.mutate({
      tracks: toDescriptors(tracks),
      k,
      playlistId: playlist.id,
      playlistName: playlist.name,
    });
  }

  return {
    k,
    setK,
    canSplit,
    clusters,
    isSplit: clusters !== null,
    running,
    error,
    skipped: job.data?.result?.skipped.length ?? 0,
    progress: job.data
      ? { done: job.data.done, total: job.data.total, phase: job.data.phase }
      : null,
    run,
    reset: () => {
      start.reset();
      setAdopted(undefined);
    },
  };
}

export type MoodSplit = ReturnType<typeof useMoodSplit>;
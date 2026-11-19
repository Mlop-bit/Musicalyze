"use client";

import { Popover } from "@base-ui/react/popover";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity } from "lucide-react";
import { useRouter } from "next/navigation";
import { Tip } from "@/components/ui/tip";
import { authClient } from "@/lib/auth-client";
import { useTRPC } from "@/trpc/client";
import { type ActivityEntry, ActivityItem } from "./activity-item";

const FAST_POLL_MS = 2500;
const SLOW_POLL_MS = 20000;

export function ActivityMenu() {
  const trpc = useTRPC();
  const router = useRouter();
  const queryClient = useQueryClient();
  const { data: session } = authClient.useSession();
  const jobs = useQuery(
    trpc.jobs.list.queryOptions(undefined, {
      enabled: !!session,
      refetchInterval: (query) =>
        query.state.data?.some(
          (job) => job.status === "queued" || job.status === "running",
        )
          ? FAST_POLL_MS
          : SLOW_POLL_MS,
    }),
  );
  const remove = useMutation(
    trpc.jobs.remove.mutationOptions({
      onSuccess: () =>
        queryClient.invalidateQueries(trpc.jobs.list.queryFilter()),
    }),
  );

  if (!session) return null;

  const entries = jobs.data ?? [];
  const running = entries.filter(
    (job) => job.status === "queued" || job.status === "running",
  ).length;

  function open(entry: ActivityEntry) {
    const params = new URLSearchParams({
      job: entry.id,
      kind: entry.kind,
      playlist: entry.playlistId ?? "",
    });
    router.push(`/dashboard?${params}`);
  }

  return (
    <Popover.Root>
      <Tip
        label="Background jobs: orderings and searches keep running here even if you close the page."
        side="bottom"
      >
        <Popover.Trigger
          aria-label={running > 0 ? `${running} jobs running` : "Activity"}
          className="press relative flex size-9 items-center justify-center rounded-full text-muted-foreground outline-none hover:text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/40"
        >
          <Activity className="size-5" />
          {running > 0 && (
            <span className="absolute right-0.5 top-0.5 flex size-4 items-center justify-center rounded-full bg-brand text-[0.65rem] font-semibold text-brand-foreground">
              {running}
            </span>
          )}
        </Popover.Trigger>
      </Tip>
      <Popover.Portal>
        <Popover.Positioner sideOffset={10} align="end" className="z-50">
          <Popover.Popup className="surface w-80 rounded-2xl p-2 text-sm backdrop-blur-xl">
            <p className="px-3 pb-1 pt-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Background jobs
            </p>
            {entries.length === 0 ? (
              <p className="px-3 py-4 text-muted-foreground">
                Orderings and searches you start keep running here, even if you
                close the page.
              </p>
            ) : (
              <ul className="max-h-96 overflow-y-auto">
                {entries.map((entry) => (
                  <ActivityItem
                    key={entry.id}
                    entry={entry}
                    onOpen={open}
                    onRemove={(item) => remove.mutate({ jobId: item.id })}
                  />
                ))}
              </ul>
            )}
          </Popover.Popup>
        </Popover.Positioner>
      </Popover.Portal>
    </Popover.Root>
  );
}

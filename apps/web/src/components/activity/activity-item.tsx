import { X } from "lucide-react";
import { formatRelativeDate } from "@/lib/format-relative-date";

export type ActivityEntry = {
  id: string;
  kind: string;
  title: string;
  playlistId: string | null;
  createdAt: string;
  status: "queued" | "running" | "succeeded" | "failed";
  phase: "resolving" | "computing" | null;
  done: number;
  total: number;
  error: string | null;
};

type Props = {
  entry: ActivityEntry;
  onOpen: (entry: ActivityEntry) => void;
  onRemove: (entry: ActivityEntry) => void;
};

function statusText(entry: ActivityEntry) {
  if (entry.status === "queued") return "Waiting for the worker";
  if (entry.status === "running") {
    const phase = entry.phase === "computing" ? "Computing" : "Listening";
    return entry.total > 0
      ? `${phase} · ${entry.done}/${entry.total}`
      : `${phase}…`;
  }
  if (entry.status === "failed") return entry.error ?? "Failed";
  return "Ready";
}

function statusTone(status: ActivityEntry["status"]) {
  if (status === "failed") return "text-destructive";
  if (status === "succeeded") return "text-brand";
  return "text-muted-foreground";
}

export function ActivityItem({ entry, onOpen, onRemove }: Props) {
  const finished = entry.status === "succeeded" || entry.status === "failed";
  const openable = entry.status === "succeeded" && entry.playlistId !== null;
  const fraction = entry.total > 0 ? entry.done / entry.total : 0;

  return (
    <li className="group relative">
      <button
        type="button"
        disabled={!openable}
        onClick={() => onOpen(entry)}
        className="flex w-full flex-col gap-1 rounded-xl px-3 py-2 text-left transition-colors enabled:hover:bg-accent"
      >
        <span className="truncate pr-6 text-sm font-medium">{entry.title}</span>
        <span className={`truncate text-xs ${statusTone(entry.status)}`}>
          {statusText(entry)} · {formatRelativeDate(entry.createdAt)}
        </span>
        {entry.status === "running" && (
          <span className="mt-0.5 h-1 overflow-hidden rounded-full bg-foreground/10">
            <span
              className="block h-full rounded-full bg-brand transition-[width] duration-700"
              style={{ width: `${Math.max(fraction, 0.05) * 100}%` }}
            />
          </span>
        )}
      </button>
      {finished && (
        <button
          type="button"
          aria-label={`Remove ${entry.title}`}
          onClick={() => onRemove(entry)}
          className="absolute right-2 top-2 rounded-full p-1 text-muted-foreground opacity-0 transition-opacity hover:text-foreground focus-visible:opacity-100 group-hover:opacity-100"
        >
          <X className="size-3.5" />
        </button>
      )}
    </li>
  );
}

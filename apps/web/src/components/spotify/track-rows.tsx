"use client";

import { ExternalLink, Loader2, Pause, Play, Sparkles } from "lucide-react";
import { useMemo } from "react";
import { RemoteImage } from "@/components/ui/remote-image";
import { normalizeLevels } from "@/lib/mood-color";
import { formatDuration } from "@/lib/playlist-stats";
import { withKeys } from "@/lib/track-keys";
import type { TrackDetail } from "@/server/ml/schema";
import type { PlaylistTrack } from "@/server/spotify/schema";
import { MoodChip } from "./mood-chip";
import { usePreview } from "./preview-player";

type Props = {
  tracks: PlaylistTrack[];
  details?: Map<string, TrackDetail>;
  trailing?: (track: PlaylistTrack) => React.ReactNode;
  onFindSimilar?: (track: PlaylistTrack) => void;
  compact?: boolean;
};

function PlayIcon({ status }: { status: string }) {
  if (status === "loading") return <Loader2 className="size-4 animate-spin" />;
  if (status === "playing") return <Pause className="size-4 fill-current" />;
  return <Play className="size-4 fill-current" />;
}

export function TrackRows({
  tracks,
  details,
  trailing,
  onFindSimilar,
  compact = false,
}: Props) {
  const { statusOf, toggle } = usePreview();
  const keyed = useMemo(() => withKeys(tracks), [tracks]);
  const levels = useMemo(
    () =>
      normalizeLevels(
        tracks.map((track) => details?.get(track.id ?? "")?.energy ?? null),
      ),
    [tracks, details],
  );

  return (
    <ol className={compact ? "divide-y divide-border" : ""}>
      {keyed.map(({ key, track }, index) => {
        const status = statusOf(track);
        const active = status === "playing" || status === "loading";
        const detail = details?.get(track.id ?? "");
        return (
          <li key={key}>
            <div
              className={`group flex items-center gap-3 rounded-xl px-2.5 transition-colors hover:bg-accent ${compact ? "py-3" : "py-1.5"} ${active ? "bg-brand/10" : ""}`}
            >
              <button
                type="button"
                onClick={() => toggle(track)}
                aria-label={
                  status === "playing"
                    ? `Pause ${track.name}`
                    : `Play preview of ${track.name}`
                }
                className="flex min-w-0 flex-1 items-center gap-3 text-left outline-none focus-visible:ring-[3px] focus-visible:ring-ring/40"
              >
                {!compact && (
                  <span className="w-7 text-right text-xs tabular-nums text-muted-foreground">
                    {index + 1}
                  </span>
                )}
                <span className="relative size-10 shrink-0 overflow-hidden rounded-lg bg-muted">
                  {track.image && (
                    <RemoteImage src={track.image} sizes="40px" />
                  )}
                  <span
                    className={`absolute inset-0 flex items-center justify-center bg-black/50 text-white transition-opacity ${active ? "opacity-100" : "opacity-0 group-hover:opacity-100"}`}
                  >
                    <PlayIcon status={status} />
                  </span>
                </span>
                <span className="min-w-0 flex-1">
                  <span
                    className={`block truncate text-sm font-medium ${active ? "text-brand" : ""}`}
                  >
                    {track.name}
                  </span>
                  <span className="block truncate text-xs text-muted-foreground">
                    {status === "unavailable"
                      ? "No preview available for this track"
                      : track.artists}
                  </span>
                </span>
              </button>
              {detail && (
                <MoodChip label={detail.mood_label} level={levels[index]} />
              )}
              {!compact && (
                <span className="hidden w-48 truncate text-xs text-muted-foreground md:block">
                  {track.album}
                </span>
              )}
              <span className="w-10 text-right text-xs tabular-nums text-muted-foreground">
                {formatDuration(track.durationMs)}
              </span>
              {onFindSimilar && (
                <button
                  type="button"
                  aria-label={`Find tracks similar to ${track.name}`}
                  title="Find similar"
                  onClick={() => onFindSimilar(track)}
                  className="text-muted-foreground opacity-0 transition-opacity hover:text-brand focus-visible:opacity-100 group-hover:opacity-100"
                >
                  <Sparkles className="size-3.5" />
                </button>
              )}
              <a
                href={track.url}
                target="_blank"
                rel="noreferrer"
                aria-label={`Open ${track.name} on Spotify`}
                className="text-muted-foreground opacity-0 transition-opacity hover:text-foreground focus-visible:opacity-100 group-hover:opacity-100"
              >
                <ExternalLink className="size-3.5" />
              </a>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

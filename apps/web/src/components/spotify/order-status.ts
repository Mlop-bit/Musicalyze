import type { Playlist } from "@/server/spotify/schema";
import type { MoodOrder } from "./use-mood-order";

export type StatusLine = { text: string; isError: boolean };

export function orderStatus(playlist: Playlist, mood: MoodOrder): StatusLine {
  if (mood.error) return { text: mood.error, isError: true };
  if (mood.running) {
    const phase =
      mood.progress?.phase === "computing"
        ? "Computing the order"
        : "Analysing tracks";
    const counts = mood.progress
      ? ` · ${mood.progress.done}/${mood.progress.total}`
      : "";
    return { text: `${phase}${counts}`, isError: false };
  }
  if (mood.isOrdered) {
    const skipped =
      mood.skipped > 0 ? ` (${mood.skipped} could not be analysed)` : "";
    return {
      text: `Ordered by mood, save this order to Spotify?${skipped}`,
      isError: false,
    };
  }
  return { text: playlist.owner ?? "Spotify", isError: false };
}

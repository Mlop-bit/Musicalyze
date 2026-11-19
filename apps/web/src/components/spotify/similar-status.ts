import type { StatusLine } from "./order-status";
import type { Recommend } from "./use-recommend";

export function similarStatus(similar: Recommend): StatusLine {
  if (similar.error) return { text: similar.error, isError: true };
  if (similar.running) {
    const phase =
      similar.progress?.phase === "computing"
        ? "Comparing the sound"
        : "Listening to your library";
    const counts = similar.progress
      ? ` · ${similar.progress.done}/${similar.progress.total}`
      : "";
    return { text: `${phase}${counts}`, isError: false };
  }
  const dropped =
    similar.dropped > 0
      ? ` (${similar.dropped} candidates left out to keep it quick)`
      : "";
  const subject = similar.label ? ` to ${similar.label}` : "";
  return {
    text:
      similar.tracks.length > 0
        ? `${similar.tracks.length} tracks similar${subject}${dropped}`
        : "No similar tracks found yet",
    isError: false,
  };
}

import { MatchChip } from "./match-chip";
import { TrackRows } from "./track-rows";
import type { Recommend } from "./use-recommend";

type ListState = Pick<Recommend, "running" | "error" | "tracks" | "candidates">;

export function SimilarList({ similar }: { similar: ListState }) {
  if (similar.running) {
    return (
      <p className="p-4 text-sm text-muted-foreground">
        Checking {similar.candidates || "your"} tracks from your other playlists
        against this one. New tracks take a moment each.
      </p>
    );
  }
  if (similar.error) return null;
  if (similar.tracks.length === 0) {
    return (
      <p className="p-4 text-sm text-muted-foreground">
        Nothing close enough yet. Other playlists need more analysed tracks.
      </p>
    );
  }
  const matches = new Map(
    similar.tracks.map((track) => [track.id, track.similarity]),
  );

  return (
    <TrackRows
      tracks={similar.tracks}
      trailing={(track) => {
        const similarity = matches.get(track.id);
        return similarity === undefined ? null : (
          <MatchChip similarity={similarity} />
        );
      }}
    />
  );
}

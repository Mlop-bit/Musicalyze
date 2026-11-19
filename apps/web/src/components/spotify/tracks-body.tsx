import type { PlaylistTrack } from "@/server/spotify/schema";
import { SimilarList } from "./similar-list";
import { TrackError } from "./track-error";
import { TrackRows } from "./track-rows";
import type { MoodOrder } from "./use-mood-order";
import type { Recommend } from "./use-recommend";

type TracksQuery = {
  isPending: boolean;
  error: { message: string } | null;
  data: PlaylistTrack[] | undefined;
};

type Props = {
  query: TracksQuery;
  mood: MoodOrder;
  similar: Recommend;
  compact?: boolean;
};

function Note({ children }: { children: React.ReactNode }) {
  return <p className="p-4 text-sm text-muted-foreground">{children}</p>;
}

export function TracksBody({ query, mood, similar, compact = false }: Props) {
  if (similar.active) return <SimilarList similar={similar} />;
  if (query.isPending) return <Note>Loading tracks…</Note>;
  if (query.error) return <TrackError message={query.error.message} />;
  if (mood.ordered.length === 0) return <Note>This playlist is empty.</Note>;

  return (
    <TrackRows
      tracks={mood.ordered}
      details={mood.details}
      onFindSimilar={(track) => similar.run(track.id ?? undefined, track.name)}
      compact={compact}
    />
  );
}

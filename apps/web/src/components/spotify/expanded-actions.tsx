import { Button } from "@/components/ui/button";
import { Tip } from "@/components/ui/tip";
import type { Playlist } from "@/server/spotify/schema";
import { DiscoverButton } from "./discover-button";
import { FindSimilarButton } from "./find-similar-button";
import { ModeSelect } from "./mode-select";
import { OrderDecision } from "./order-decision";
import { SimilarControls } from "./similar-controls";
import type { MoodOrder } from "./use-mood-order";
import type { MoodSplit } from "./use-mood-split";
import type { Recommend } from "./use-recommend";

type Props = {
  playlist: Playlist;
  mood: MoodOrder;
  similar: Recommend;
  split: MoodSplit;
};

export function ExpandedActions({ playlist, mood, similar, split }: Props) {
  if (similar.active) {
    return <SimilarControls playlist={playlist} similar={similar} size="sm" />;
  }
  if (split.isSplit) {
    return (
      <Button
        type="button"
        size="sm"
        variant="outline"
        className="h-8 rounded-lg"
        onClick={split.reset}
      >
        ← Back to playlist
      </Button>
    );
  }
  if (mood.isOrdered) {
    return (
      <OrderDecision
        playlist={playlist}
        ordered={mood.ordered}
        onDone={mood.reset}
      />
    );
  }
  const empty = mood.ordered.length === 0;
  const busy = mood.running || split.running;

  return (
    <div className="flex w-full flex-wrap items-center justify-between gap-2">
      <div className="flex flex-wrap items-center gap-1.5">
        <ModeSelect
          value={mood.mode}
          onValueChange={mood.setMode}
          disabled={busy}
        />
        <Tip label="Reorders the playlist by how the tracks sound. You review the result first, nothing changes on Spotify until you save.">
          <Button
            type="button"
            size="sm"
            className="h-8 rounded-lg font-medium"
            disabled={busy || mood.ordered.length < 2}
            onClick={mood.run}
          >
            {mood.running ? "Ordering…" : "Order by mood"}
          </Button>
        </Tip>
        <Tip label="Splits the playlist into mood-based sub-playlists (requires at least 6 tracks).">
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="h-8 rounded-lg hover:bg-accent/60"
            disabled={busy || !split.canSplit}
            onClick={split.run}
          >
            {split.running ? "Splitting…" : "Split by mood"}
          </Button>
        </Tip>
      </div>

      <div className="flex items-center gap-1.5">
        <FindSimilarButton
          size="sm"
          onClick={() => similar.run()}
          disabled={busy || empty}
        />
        <DiscoverButton
          size="sm"
          onClick={() => similar.run(undefined, undefined, "discover")}
          disabled={busy || empty}
        />
      </div>
    </div>
  );
}

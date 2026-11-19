import { Button } from "@/components/ui/button";
import { Tip } from "@/components/ui/tip";
import type { Playlist } from "@/server/spotify/schema";
import { DiscoverButton } from "./discover-button";
import { FindSimilarButton } from "./find-similar-button";
import { ModeSelect } from "./mode-select";
import { OrderDecision } from "./order-decision";
import { SimilarControls } from "./similar-controls";
import type { MoodOrder } from "./use-mood-order";
import type { Recommend } from "./use-recommend";

type Props = { playlist: Playlist; mood: MoodOrder; similar: Recommend };

export function ExpandedActions({ playlist, mood, similar }: Props) {
  if (similar.active) {
    return <SimilarControls playlist={playlist} similar={similar} size="sm" />;
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

  return (
    <>
      <ModeSelect
        value={mood.mode}
        onValueChange={mood.setMode}
        disabled={mood.running}
      />
      <FindSimilarButton
        size="sm"
        onClick={() => similar.run()}
        disabled={mood.running || empty}
      />
      <DiscoverButton
        size="sm"
        onClick={() => similar.run(undefined, undefined, "discover")}
        disabled={mood.running || empty}
      />
      <Tip label="Reorders the playlist by how the tracks sound. You review the result first, nothing changes on Spotify until you save.">
        <Button
          type="button"
          size="sm"
          disabled={mood.running || mood.ordered.length < 2}
          onClick={mood.run}
        >
          {mood.running ? "Ordering…" : "Order by mood"}
        </Button>
      </Tip>
    </>
  );
}

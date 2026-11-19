import type { Playlist } from "@/server/spotify/schema";
import { DiscoverButton } from "./discover-button";
import { FindSimilarButton } from "./find-similar-button";
import { OrderControls } from "./order-controls";
import { SimilarControls } from "./similar-controls";
import type { MoodOrder } from "./use-mood-order";
import type { Recommend } from "./use-recommend";

type Props = {
  playlist: Playlist;
  mood: MoodOrder;
  similar: Recommend;
  trackCount: number;
};

export function BarControls({ playlist, mood, similar, trackCount }: Props) {
  if (similar.active) {
    return <SimilarControls playlist={playlist} similar={similar} />;
  }
  const searchDisabled = mood.running || trackCount === 0;

  return (
    <>
      {!mood.isOrdered && (
        <>
          <FindSimilarButton
            iconOnly
            onClick={() => similar.run()}
            disabled={searchDisabled}
          />
          <DiscoverButton
            iconOnly
            onClick={() => similar.run(undefined, undefined, "discover")}
            disabled={searchDisabled}
          />
        </>
      )}
      <OrderControls playlist={playlist} mood={mood} trackCount={trackCount} />
    </>
  );
}

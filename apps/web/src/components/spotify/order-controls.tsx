"use client";

import { ArrowDownUp } from "lucide-react";
import ShinyText from "@/components/react-bits/ShinyText";
import { Button } from "@/components/ui/button";
import { Tip } from "@/components/ui/tip";
import type { Playlist } from "@/server/spotify/schema";
import { ModeSelect } from "./mode-select";
import { OrderDecision } from "./order-decision";
import type { MoodOrder } from "./use-mood-order";

type Props = { playlist: Playlist; mood: MoodOrder; trackCount: number };

export function OrderControls({ playlist, mood, trackCount }: Props) {
  if (mood.isOrdered) {
    return (
      <OrderDecision
        playlist={playlist}
        ordered={mood.ordered}
        onDone={mood.reset}
        size="lg"
      />
    );
  }

  return (
    <div className="flex items-center gap-2">
      <ModeSelect
        value={mood.mode}
        onValueChange={mood.setMode}
        disabled={mood.running}
      />
      <Tip label="Reorders the playlist by how the tracks sound. You review the result first, nothing changes on Spotify until you save.">
        <Button
          type="button"
          size="lg"
          disabled={mood.running || trackCount < 2}
          onClick={mood.run}
          className="h-12 gap-2 px-7 text-base font-semibold shadow-xl shadow-brand/40"
        >
          {mood.running ? (
            <ShinyText
              text="Ordering…"
              color="#08130c"
              shineColor="#ffffff"
              speed={1.6}
            />
          ) : (
            <>
              <ArrowDownUp className="size-4" />
              Order by mood
            </>
          )}
        </Button>
      </Tip>
    </div>
  );
}

import type { Playlist } from "@/server/spotify/schema";
import { PlaylistCover } from "./playlist-cover";

type Props = { playlist: Playlist; selected: boolean; onSelect: () => void };

export function PlaylistCard({ playlist, selected, onSelect }: Props) {
  return (
    <button
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
      className="press flex w-full items-center gap-3 rounded-2xl p-2 text-left hover:bg-accent aria-pressed:bg-brand/15 aria-pressed:ring-1 aria-pressed:ring-brand"
    >
      <PlaylistCover
        playlist={playlist}
        className="size-12 shrink-0 rounded-xl"
      />
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-semibold">
          {playlist.name}
        </span>
        <span className="block truncate text-xs text-muted-foreground">
          {playlist.trackCount} tracks
          {playlist.owner ? ` · ${playlist.owner}` : ""}
        </span>
      </span>
    </button>
  );
}

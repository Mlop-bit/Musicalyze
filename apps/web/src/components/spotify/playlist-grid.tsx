"use client";

import type { Playlist } from "@/server/spotify/schema";
import { ExpandedPlaylist } from "./expanded-playlist";
import { PlaylistCover } from "./playlist-cover";

type Props = {
  playlists: Playlist[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
};

export function PlaylistGrid({ playlists, selectedId, onSelect }: Props) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {playlists.map((playlist) => {
        const open = playlist.id === selectedId;
        return (
          <article
            key={playlist.id}
            className="surface self-start overflow-hidden rounded-2xl"
          >
            <button
              type="button"
              aria-expanded={open}
              onClick={() => onSelect(open ? null : playlist.id)}
              className="flex w-full items-center gap-4 p-4 text-left transition hover:bg-background/60"
            >
              <PlaylistCover
                playlist={playlist}
                className="h-16 w-16 rounded-lg"
              />
              <span className="min-w-0 flex-1">
                <span className="block truncate font-semibold">
                  {playlist.name}
                </span>
                <span className="mt-1 block text-sm text-muted-foreground">
                  {playlist.trackCount} tracks
                </span>
              </span>
              <span className="text-muted-foreground">{open ? "−" : "+"}</span>
            </button>
            {open && <ExpandedPlaylist playlist={playlist} />}
          </article>
        );
      })}
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { authClient } from "@/lib/auth-client";
import { LIKED_ID } from "@/server/spotify/schema";
import { useTRPC } from "@/trpc/client";
import { PlaylistCard } from "./playlist-card";
import {
  PlaylistFilters,
  usePlaylistFilters,
  type View,
  ViewToggle,
} from "./playlist-filters";
import { PlaylistGrid } from "./playlist-grid";
import { PreviewProvider } from "./preview-player";
import { TrackPanel } from "./track-panel";

export function PlaylistsApp() {
  return (
    <PreviewProvider>
      <PlaylistsView />
    </PreviewProvider>
  );
}

function PlaylistsView() {
  const trpc = useTRPC();
  const { data: session } = authClient.useSession();
  const playlistsQuery = useQuery(trpc.spotify.playlists.queryOptions());
  const playlists = playlistsQuery.data ?? [];
  const filters = usePlaylistFilters(playlists, session?.user.name);
  const [view, setView] = useState<View>("grid");
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const selected =
    playlists.find((playlist) => playlist.id === selectedId) ?? null;
  const pinned =
    filters.visible.find((playlist) => playlist.id === LIKED_ID) ?? null;
  const rest = filters.visible.filter((playlist) => playlist.id !== LIKED_ID);
  const status = playlistsQuery.isPending ? (
    <p className="text-sm text-muted-foreground">Loading your playlists…</p>
  ) : filters.visible.length === 0 ? (
    <p className="text-sm text-muted-foreground">No playlists match.</p>
  ) : null;
  const error = playlistsQuery.error && (
    <p role="alert" className="text-sm text-destructive">
      {playlistsQuery.error.message}
    </p>
  );

  if (view === "grid") {
    return (
      <div className="h-full overflow-y-auto px-6 pb-8 lg:px-14">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-muted-foreground">
              YOUR SPOTIFY LIBRARY
            </p>
            <h1 className="mt-2 text-4xl font-semibold tracking-tight">
              Your playlists
            </h1>
          </div>
          <ViewToggle view={view} onViewChange={setView} />
        </div>
        <div className="mb-6">
          <PlaylistFilters filters={filters} />
        </div>
        {error}
        {status}
        <PlaylistGrid
          playlists={filters.visible}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
      </div>
    );
  }

  return (
    <div className="grid h-full gap-3 overflow-y-auto p-3 lg:grid-cols-[minmax(0,22rem)_minmax(0,1fr)] lg:overflow-hidden">
      <aside className="surface flex min-h-0 flex-col gap-4 rounded-3xl p-4">
        <div className="flex items-center justify-between gap-2">
          <h1 className="font-script text-4xl leading-none">Your crate</h1>
          <ViewToggle view={view} onViewChange={setView} />
        </div>
        <PlaylistFilters filters={filters} />
        {error}
        {status}
        <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-1.5">
          {pinned && (
            <PlaylistCard
              playlist={pinned}
              selected={pinned.id === selectedId}
              onSelect={() => setSelectedId(pinned.id)}
            />
          )}
          {rest.length > 0 && (
            <div className="space-y-1.5">
              <p className="px-2 text-xs font-medium text-muted-foreground">
                Playlists · {rest.length}
              </p>
              {rest.map((playlist) => (
                <PlaylistCard
                  key={playlist.id}
                  playlist={playlist}
                  selected={playlist.id === selectedId}
                  onSelect={() => setSelectedId(playlist.id)}
                />
              ))}
            </div>
          )}
        </div>
      </aside>
      <TrackPanel key={selected?.id ?? "none"} playlist={selected} />
    </div>
  );
}

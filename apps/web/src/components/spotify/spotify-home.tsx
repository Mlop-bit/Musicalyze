"use client";

import { useEffect, useState } from "react";
import { authClient } from "@/lib/auth-client";

type Playlist = {
  id: string;
  name: string;
  description: string | null;
  image: string | null;
  url: string;
  owner: string | null;
  trackCount: number;
};

type PlaylistTrack = {
  id: string | null;
  name: string;
  artists: string;
  album: string;
  image: string | null;
  url: string;
  durationMs: number;
};

export function SpotifyHome() {
  const { data: session, isPending } = authClient.useSession();
  const [playlists, setPlaylists] = useState<Playlist[]>([]);
  const [tracks, setTracks] = useState<PlaylistTrack[]>([]);
  const [selectedPlaylist, setSelectedPlaylist] = useState<string | null>(null);
  const [loadingPlaylists, setLoadingPlaylists] = useState(false);
  const [loadingTracks, setLoadingTracks] = useState(false);
  const [signingIn, setSigningIn] = useState(false);
  const [error, setError] = useState("");
  const [signInError, setSignInError] = useState("");

  useEffect(() => {
    if (!session) return;
    const controller = new AbortController();
    setLoadingPlaylists(true);
    fetch("/api/spotify/playlists", { signal: controller.signal })
      .then(async (response) => {
        const data = (await response.json()) as { playlists?: Playlist[]; error?: string };
        if (!response.ok) throw new Error(data.error ?? "Could not load playlists.");
        setPlaylists(data.playlists ?? []);
      })
      .catch((cause: unknown) => {
        if (!controller.signal.aborted) {
          setError(cause instanceof Error ? cause.message : "Could not load playlists.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoadingPlaylists(false);
      });
    return () => controller.abort();
  }, [session]);

  async function togglePlaylist(playlist: Playlist) {
    if (selectedPlaylist === playlist.id) {
      setSelectedPlaylist(null);
      setTracks([]);
      return;
    }
    setSelectedPlaylist(playlist.id);
    setTracks([]);
    setError("");
    setLoadingTracks(true);
    try {
      const response = await fetch(`/api/spotify/playlists/${encodeURIComponent(playlist.id)}/tracks`);
      const data = (await response.json()) as { tracks?: PlaylistTrack[]; error?: string };
      if (!response.ok) throw new Error(data.error ?? "Could not load playlist tracks.");
      setTracks(data.tracks ?? []);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load playlist tracks.");
    } finally {
      setLoadingTracks(false);
    }
  }

  async function signIn() {
    setSignInError("");
    setSigningIn(true);
    try {
      const result = await authClient.signIn.social({ provider: "spotify", callbackURL: "/" });
      if (result.error) {
        setSignInError(result.error.message);
        setSigningIn(false);
      }
    } catch (cause) {
      setSignInError(cause instanceof Error ? cause.message : "Spotify sign-in could not start.");
      setSigningIn(false);
    }
  }

  async function signOut() {
    await authClient.signOut();
    setPlaylists([]);
    setSelectedPlaylist(null);
    setTracks([]);
  }

  return (
    <main className="min-h-screen px-5 py-8 sm:px-10 sm:py-12">
      <div className="mx-auto max-w-6xl">
        <header className="mb-16 flex items-center justify-between">
          <a href="/" className="text-xl font-semibold tracking-tight">Musicalyze</a>
          {session && (
            <div className="flex items-center gap-4 text-sm">
              <span className="hidden text-muted-foreground sm:inline">{session.user.name}</span>
              <button onClick={signOut} className="rounded-full border border-border px-4 py-2 hover:bg-card">Log out</button>
            </div>
          )}
        </header>

        {isPending ? (
          <p className="py-20 text-center text-sm text-muted-foreground">Loading…</p>
        ) : !session ? (
          <section className="mx-auto flex max-w-lg flex-col items-center py-24 text-center">
            <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-full bg-[#1ed760] text-2xl font-bold text-black">♪</div>
            <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Your music, in one place.</h1>
            <p className="mt-4 max-w-sm text-muted-foreground">Connect Spotify to browse your playlists and the tracks inside them.</p>
            <button type="button" onClick={() => void signIn()} disabled={signingIn} className="mt-8 rounded-full bg-[#1ed760] px-7 py-3 font-semibold text-black transition hover:bg-[#1ed760]/90 disabled:cursor-wait disabled:opacity-70">
              {signingIn ? "Connecting…" : "Continue with Spotify"}
            </button>
            {signInError && <p role="alert" className="mt-4 max-w-md text-sm text-red-700">Could not start Spotify sign-in: {signInError}</p>}
          </section>
        ) : (
          <section>
            <div className="mb-8">
              <p className="text-sm font-medium text-muted-foreground">YOUR SPOTIFY LIBRARY</p>
              <h1 className="mt-2 text-4xl font-semibold tracking-tight">Your playlists</h1>
            </div>

            {error && <p role="alert" className="mb-6 rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800">{error}</p>}
            {loadingPlaylists ? (
              <p className="py-12 text-sm text-muted-foreground">Loading your playlists…</p>
            ) : playlists.length === 0 ? (
              <p className="py-12 text-muted-foreground">No playlists found in this Spotify account.</p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {playlists.map((playlist) => (
                  <article key={playlist.id} className="overflow-hidden rounded-2xl border border-border bg-card">
                    <button onClick={() => void togglePlaylist(playlist)} aria-expanded={selectedPlaylist === playlist.id} className="flex w-full items-center gap-4 p-4 text-left transition hover:bg-background/60">
                      {playlist.image ? (
                        // Spotify image URLs are temporary, so use a regular image element.
                        // biome-ignore lint/performance/noImgElement: Spotify supplies temporary external artwork URLs.
                        <img src={playlist.image} alt="" className="h-16 w-16 rounded-lg object-cover" />
                      ) : <div className="h-16 w-16 rounded-lg bg-background" />}
                      <span className="min-w-0 flex-1">
                        <span className="block truncate font-semibold">{playlist.name}</span>
                        <span className="mt-1 block text-sm text-muted-foreground">{playlist.trackCount} tracks</span>
                      </span>
                      <span className="text-muted-foreground">{selectedPlaylist === playlist.id ? "−" : "+"}</span>
                    </button>

                    {selectedPlaylist === playlist.id && (
                      <div className="border-t border-border px-4 py-3">
                        {loadingTracks ? (
                          <p className="py-3 text-sm text-muted-foreground">Loading tracks…</p>
                        ) : tracks.length === 0 ? (
                          <p className="py-3 text-sm text-muted-foreground">This playlist is empty.</p>
                        ) : (
                          <ul className="max-h-80 divide-y divide-border overflow-y-auto">
                            {tracks.map((track, index) => (
                              <li key={`${track.id ?? track.name}-${index}`}>
                                <a href={track.url} target="_blank" rel="noreferrer" className="flex items-center gap-3 py-3 hover:text-signal-violet">
                                  {track.image ? (
                                    // biome-ignore lint/performance/noImgElement: Spotify supplies temporary external artwork URLs.
                                    <img src={track.image} alt="" className="h-10 w-10 rounded object-cover" />
                                  ) : <div className="h-10 w-10 rounded bg-background" />}
                                  <span className="min-w-0 flex-1">
                                    <span className="block truncate text-sm font-medium">{track.name}</span>
                                    <span className="block truncate text-xs text-muted-foreground">{track.artists}</span>
                                  </span>
                                  <span className="shrink-0 text-xs text-muted-foreground">{formatDuration(track.durationMs)}</span>
                                </a>
                              </li>
                            ))}
                          </ul>
                        )}
                        <button type="button" disabled title="Mood ordering is not available yet" className="mt-3 inline-block cursor-not-allowed text-xs font-medium text-muted-foreground">
                          Order by mood
                        </button>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  );
}

function formatDuration(durationMs: number) {
  const totalSeconds = Math.floor(durationMs / 1000);
  return `${Math.floor(totalSeconds / 60)}:${String(totalSeconds % 60).padStart(2, "0")}`;
}

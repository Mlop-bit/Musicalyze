"use client";

import { useState, type FormEvent } from "react";

type TrackResult = {
  musicbrainz_id: string | null;
  bpm: number | null;
  key: string | null;
  mood_label: string | null;
};

export function TrackSearch() {
  const [search, setSearch] = useState("");
  const [result, setResult] = useState<TrackResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = search.trim();
    if (!value) return;

    setError("");
    setResult(null);
    setLoading(true);
    const isMusicBrainzId = /^[\da-f]{8}-(?:[\da-f]{4}-){3}[\da-f]{12}$/i.test(value);

    try {
      const response = await fetch("/api/tracks/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          isMusicBrainzId ? { musicbrainz_id: value } : { query: value },
        ),
      });
      const data = (await response.json()) as TrackResult | { detail?: string };
      if (!response.ok) {
        setError("detail" in data ? data.detail ?? "Search failed." : "Search failed.");
      } else {
        setResult(data as TrackResult);
      }
    } catch {
      setError("Could not reach the search service.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-[75vh] items-center justify-center px-5 pb-16 pt-28">
      <div className="w-full max-w-xl">
        <h1 className="mb-6 text-center text-3xl font-semibold tracking-tight">
          Search for a song
        </h1>
        <form onSubmit={onSubmit} className="flex gap-2">
          <input
            aria-label="Song, artist, or MusicBrainz ID"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Song, artist, or MusicBrainz ID"
            className="h-12 min-w-0 flex-1 rounded-lg border border-border bg-card px-4 outline-none focus:border-signal-violet"
          />
          <button
            type="submit"
            disabled={loading || !search.trim()}
            className="h-12 rounded-lg bg-signal-violet px-5 font-medium text-white disabled:opacity-50"
          >
            {loading ? "Searching…" : "Search"}
          </button>
        </form>

        {error && <p role="alert" className="mt-4 text-center text-sm text-red-700">{error}</p>}
        {result && (
          <div className="mt-6 rounded-lg border border-border bg-card p-5 text-sm">
            <p>Tempo: {result.bpm ? `${Math.round(result.bpm)} BPM` : "Unknown"}</p>
            <p className="mt-2">Key: {result.key || "Unknown"}</p>
            <p className="mt-2">Mood: {result.mood_label || "Unknown"}</p>
          </div>
        )}
      </div>
    </main>
  );
}

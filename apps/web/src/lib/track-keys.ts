import type { PlaylistTrack } from "@/server/spotify/schema";

export type KeyedTrack = { key: string; track: PlaylistTrack };

export function withKeys(tracks: PlaylistTrack[]): KeyedTrack[] {
  const seen = new Map<string, number>();
  return tracks.map((track) => {
    const base = track.id ?? `${track.name}-${track.artists}`;
    const occurrence = seen.get(base) ?? 0;
    seen.set(base, occurrence + 1);
    return { key: `${base}-${occurrence}`, track };
  });
}

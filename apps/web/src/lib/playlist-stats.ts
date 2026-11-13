import type { PlaylistTrack } from "@/server/spotify/schema";

const TOP_ARTISTS = 3;

export function playlistStats(tracks: PlaylistTrack[]) {
  const totalMs = tracks.reduce((sum, track) => sum + track.durationMs, 0);
  const artistCounts = new Map<string, number>();
  for (const { primaryArtist } of tracks) {
    if (primaryArtist) {
      artistCounts.set(
        primaryArtist,
        (artistCounts.get(primaryArtist) ?? 0) + 1,
      );
    }
  }
  return {
    count: tracks.length,
    totalMs,
    averageMs: tracks.length ? totalMs / tracks.length : 0,
    uniqueArtists: artistCounts.size,
    topArtists: [...artistCounts]
      .sort((a, b) => b[1] - a[1])
      .slice(0, TOP_ARTISTS),
  };
}

export function sortByOrder(tracks: PlaylistTrack[], order: string[]) {
  const position = new Map(order.map((id, index) => [id, index]));
  return [...tracks].sort(
    (a, b) =>
      (position.get(a.id ?? "") ?? Number.MAX_SAFE_INTEGER) -
      (position.get(b.id ?? "") ?? Number.MAX_SAFE_INTEGER),
  );
}

export function formatDuration(durationMs: number) {
  const totalSeconds = Math.floor(durationMs / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return hours > 0
    ? `${hours}:${String(minutes).padStart(2, "0")}:${seconds}`
    : `${minutes}:${seconds}`;
}

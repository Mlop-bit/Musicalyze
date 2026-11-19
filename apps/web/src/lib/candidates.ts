import type { PlaylistTrack } from "@/server/spotify/schema";

export const CANDIDATE_CAP = 120;

export function pickCandidates(
  seeds: PlaylistTrack[],
  pools: PlaylistTrack[][],
  cap = CANDIDATE_CAP,
) {
  const seen = new Set(seeds.flatMap((track) => (track.id ? [track.id] : [])));
  const picked: PlaylistTrack[] = [];
  const longest = Math.max(0, ...pools.map((pool) => pool.length));
  for (let index = 0; index < longest && picked.length < cap; index++) {
    for (const pool of pools) {
      const track = pool[index];
      if (!track?.id || seen.has(track.id) || picked.length >= cap) continue;
      seen.add(track.id);
      picked.push(track);
    }
  }
  return picked;
}

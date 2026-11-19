import { z } from "zod";
import type { PlaylistTrack } from "@/server/spotify/schema";

const API = "https://api.deezer.com";
const RELATED_PER_ARTIST = 4;
const TRACKS_PER_ARTIST = 4;
const MAX_SEED_ARTISTS = 5;
export const DEEZER_PREFIX = "deezer:";

const idList = z.object({ data: z.array(z.object({ id: z.number() })) });
const trackSchema = z.object({
  id: z.number(),
  title: z.string(),
  duration: z.number(),
  link: z.string(),
  isrc: z.string().optional(),
  artist: z.object({ name: z.string() }),
  album: z.object({ title: z.string(), cover_medium: z.string().optional() }),
});
const topSchema = z.object({ data: z.array(trackSchema) });

async function getJson<S extends z.ZodType>(path: string, schema: S) {
  const response = await fetch(`${API}${path}`, { cache: "no-store" });
  if (!response.ok) return null;
  const parsed = schema.safeParse(await response.json());
  return parsed.success ? (parsed.data as z.infer<S>) : null;
}

export function topArtists(seeds: PlaylistTrack[]) {
  const counts = new Map<string, number>();
  for (const { primaryArtist } of seeds) {
    if (primaryArtist) {
      counts.set(primaryArtist, (counts.get(primaryArtist) ?? 0) + 1);
    }
  }
  return [...counts]
    .sort((a, b) => b[1] - a[1])
    .slice(0, MAX_SEED_ARTISTS)
    .map(([name]) => name);
}

async function artistIdByName(name: string) {
  const found = await getJson(
    `/search/artist?q=${encodeURIComponent(name)}&limit=1`,
    idList,
  );
  return found?.data[0]?.id ?? null;
}

export async function artistIdByTrackQuery(query: string) {
  const found = await getJson(
    `/search?q=${encodeURIComponent(query)}&limit=1`,
    z.object({
      data: z.array(z.object({ artist: z.object({ id: z.number() }) })),
    }),
  );
  return found?.data[0]?.artist.id ?? null;
}

function toTrack(item: z.infer<typeof trackSchema>): PlaylistTrack {
  return {
    id: `${DEEZER_PREFIX}${item.id}`,
    name: item.title,
    artists: item.artist.name,
    primaryArtist: item.artist.name,
    isrc: item.isrc ?? null,
    album: item.album.title,
    image: item.album.cover_medium ?? null,
    url: item.link,
    durationMs: item.duration * 1000,
  };
}

async function neighbourTracks(artistId: number) {
  const related = await getJson(
    `/artist/${artistId}/related?limit=${RELATED_PER_ARTIST}`,
    idList,
  );
  const artists = [artistId, ...(related?.data.map((entry) => entry.id) ?? [])];
  const tops = await Promise.all(
    artists.map((id) =>
      getJson(`/artist/${id}/top?limit=${TRACKS_PER_ARTIST}`, topSchema),
    ),
  );
  return tops.flatMap((top) => top?.data.map(toTrack) ?? []);
}

export async function discoverTracks(
  artistIds: number[],
  exclude: Set<string>,
  cap: number,
) {
  const groups = await Promise.all(artistIds.map(neighbourTracks));
  const picked = new Map<string, PlaylistTrack>();
  const longest = Math.max(0, ...groups.map((group) => group.length));
  for (let index = 0; index < longest && picked.size < cap; index++) {
    for (const group of groups) {
      const track = group[index];
      if (!track?.id || exclude.has(track.name) || picked.has(track.id))
        continue;
      picked.set(track.id, track);
      if (picked.size >= cap) break;
    }
  }
  return [...picked.values()];
}

export async function discoverFromSeeds(seeds: PlaylistTrack[], cap: number) {
  const ids = await Promise.all(topArtists(seeds).map(artistIdByName));
  const known = new Set(seeds.map((seed) => seed.name));
  return discoverTracks(
    ids.filter((id): id is number => id !== null),
    known,
    cap,
  );
}

export async function hydrateDeezerTracks(ids: string[]) {
  const found = await Promise.all(
    ids.map((id) =>
      getJson(`/track/${id.slice(DEEZER_PREFIX.length)}`, trackSchema),
    ),
  );
  return found.flatMap((item) => (item ? [toTrack(item)] : []));
}

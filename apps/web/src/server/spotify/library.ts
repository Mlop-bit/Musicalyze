import { fetchAllPages, fetchPage } from "./client";
import {
  LIKED_ID,
  likedPageSchema,
  type PlaylistTrack,
  severalTracksSchema,
  type TrackItem,
  trackPageSchema,
} from "./schema";

const API = "https://api.spotify.com/v1";
const HYDRATE_CHUNK = 50;

export function toPlaylistTrack(item: TrackItem): PlaylistTrack {
  return {
    id: item.id,
    name: item.name,
    artists: item.artists.map((artist) => artist.name).join(", "),
    primaryArtist: item.artists[0]?.name ?? "",
    isrc: item.external_ids?.isrc ?? null,
    album: item.album.name,
    image: item.album.images[0]?.url ?? null,
    url: item.external_urls.spotify,
    durationMs: item.duration_ms,
  };
}

export async function fetchPlaylistTracks(
  accessToken: string,
  playlistId: string,
): Promise<PlaylistTrack[]> {
  if (playlistId === LIKED_ID) {
    const pages = await fetchAllPages(
      `${API}/me/tracks?limit=50`,
      accessToken,
      likedPageSchema,
    );
    return pages.flatMap((page) =>
      page.items.flatMap(({ track }) =>
        track ? [toPlaylistTrack(track)] : [],
      ),
    );
  }
  const pages = await fetchAllPages(
    `${API}/playlists/${encodeURIComponent(playlistId)}/items?limit=50`,
    accessToken,
    trackPageSchema,
  );
  return pages.flatMap((page) =>
    page.items.flatMap(({ item }) => (item ? [toPlaylistTrack(item)] : [])),
  );
}

export async function hydrateTracks(
  accessToken: string,
  ids: string[],
): Promise<PlaylistTrack[]> {
  const chunks: string[][] = [];
  for (let start = 0; start < ids.length; start += HYDRATE_CHUNK) {
    chunks.push(ids.slice(start, start + HYDRATE_CHUNK));
  }
  const pages = await Promise.all(
    chunks.map((chunk) =>
      fetchPage(
        `${API}/tracks?ids=${chunk.join(",")}`,
        accessToken,
        severalTracksSchema,
      ).catch(() => null),
    ),
  );
  return pages.flatMap((page) =>
    page
      ? page.tracks.flatMap((item) => (item ? [toPlaylistTrack(item)] : []))
      : [],
  );
}

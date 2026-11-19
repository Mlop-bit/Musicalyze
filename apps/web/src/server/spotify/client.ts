import { TRPCError } from "@trpc/server";
import { z } from "zod";

export async function fetchPage<S extends z.ZodType>(
  url: string,
  accessToken: string,
  schema: S,
): Promise<z.infer<S>> {
  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
  if (!response.ok) {
    const forbidden = response.status === 401 || response.status === 403;
    throw new TRPCError({
      code: forbidden ? "FORBIDDEN" : "BAD_GATEWAY",
      message: forbidden
        ? "Spotify only lets this app read playlists you own or collaborate on."
        : `Spotify request failed with HTTP ${response.status}.`,
    });
  }
  return schema.parse(await response.json());
}

export async function fetchAllPages<
  S extends z.ZodType<{ next: string | null }>,
>(firstUrl: string, accessToken: string, schema: S): Promise<z.infer<S>[]> {
  const pages: z.infer<S>[] = [];
  let url: string | null = firstUrl;

  while (url) {
    const page: z.infer<S> = await fetchPage(url, accessToken, schema);
    pages.push(page);
    url = page.next;
  }

  return pages;
}

const WRITE_CHUNK = 100;
const EDIT_DENIED =
  "Spotify did not allow editing this playlist. Sign out and in again to grant access; only playlists you own or collaborate on can be changed.";

async function sendUris(
  urls: string[],
  accessToken: string,
  method: "PUT" | "POST",
  uris: string[],
) {
  for (const url of urls) {
    const response = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ uris }),
      cache: "no-store",
    });
    if (response.ok) return;
    if (response.status === 401 || response.status === 403) {
      throw new TRPCError({ code: "FORBIDDEN", message: EDIT_DENIED });
    }
    if (response.status !== 404) {
      throw new TRPCError({
        code: "BAD_GATEWAY",
        message: `Spotify request failed with HTTP ${response.status}.`,
      });
    }
  }
  throw new TRPCError({
    code: "NOT_FOUND",
    message: "Spotify could not find this playlist.",
  });
}

function writeInChunks(
  playlistUrl: string,
  accessToken: string,
  trackIds: string[],
  firstMethod: "PUT" | "POST",
) {
  const urls = [`${playlistUrl}/items`, `${playlistUrl}/tracks`];
  const chunks = Array.from(
    { length: Math.ceil(trackIds.length / WRITE_CHUNK) },
    (_, index) =>
      trackIds
        .slice(index * WRITE_CHUNK, (index + 1) * WRITE_CHUNK)
        .map((id) => `spotify:track:${id}`),
  );
  return chunks.reduce(
    (previous, uris, index) =>
      previous.then(() =>
        sendUris(urls, accessToken, index === 0 ? firstMethod : "POST", uris),
      ),
    Promise.resolve(),
  );
}

export function replacePlaylistTracks(
  playlistUrl: string,
  accessToken: string,
  trackIds: string[],
) {
  return writeInChunks(playlistUrl, accessToken, trackIds, "PUT");
}

export function appendPlaylistTracks(
  playlistUrl: string,
  accessToken: string,
  trackIds: string[],
) {
  return writeInChunks(playlistUrl, accessToken, trackIds, "POST");
}

const createdPlaylistSchema = z.object({
  id: z.string(),
  external_urls: z.object({ spotify: z.string() }),
});

export async function createPlaylist(
  apiBase: string,
  accessToken: string,
  name: string,
  description: string,
  trackIds: string[],
): Promise<{ id: string; url: string }> {
  const response = await fetch(`${apiBase}/me/playlists`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, description, public: false }),
    cache: "no-store",
  });
  if (!response.ok) {
    const forbidden = response.status === 401 || response.status === 403;
    throw new TRPCError({
      code: forbidden ? "FORBIDDEN" : "BAD_GATEWAY",
      message: forbidden
        ? EDIT_DENIED
        : `Spotify request failed with HTTP ${response.status}.`,
    });
  }
  const created = createdPlaylistSchema.parse(await response.json());
  if (trackIds.length > 0) {
    await appendPlaylistTracks(
      `${apiBase}/playlists/${encodeURIComponent(created.id)}`,
      accessToken,
      trackIds,
    );
  }
  return { id: created.id, url: created.external_urls.spotify };
}

import { NextResponse } from "next/server";
import { getSpotifyAccessToken } from "@/server/spotify/access-token";

type SpotifyItemsPage = {
  items: Array<{
    item: {
      id: string | null;
      name: string;
      duration_ms: number;
      artists: Array<{ name: string }>;
      album: { name: string; images: Array<{ url: string }> };
      external_urls: { spotify: string };
    } | null;
  }>;
  next: string | null;
};

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ playlistId: string }> },
) {
  try {
    const accessToken = await getSpotifyAccessToken();
    if (!accessToken) {
      return NextResponse.json({ error: "Sign in with Spotify to see playlist tracks." }, { status: 401 });
    }

    const { playlistId } = await params;
    const tracks: Array<{
      id: string | null;
      name: string;
      artists: string;
      album: string;
      image: string | null;
      url: string;
      durationMs: number;
    }> = [];
    let url: string | null = `https://api.spotify.com/v1/playlists/${encodeURIComponent(playlistId)}/items?limit=50`;

    while (url) {
      const response: Response = await fetch(url, {
        headers: { Authorization: `Bearer ${accessToken}` },
        cache: "no-store",
      });
      if (!response.ok) {
        return NextResponse.json({ error: "Spotify could not load this playlist." }, { status: response.status });
      }
      const page = (await response.json()) as SpotifyItemsPage;
      tracks.push(
        ...page.items.flatMap(({ item }) =>
          item && "album" in item
            ? [{
                id: item.id,
                name: item.name,
                artists: item.artists.map((artist) => artist.name).join(", "),
                album: item.album.name,
                image: item.album.images[0]?.url ?? null,
                url: item.external_urls.spotify,
                durationMs: item.duration_ms,
              }]
            : [],
        ),
      );
      url = page.next;
    }

    return NextResponse.json({ tracks });
  } catch {
    return NextResponse.json({ error: "Could not load playlist tracks." }, { status: 502 });
  }
}

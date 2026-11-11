import { NextResponse } from "next/server";
import { getSpotifyAccessToken } from "@/server/spotify/access-token";

type SpotifyPlaylistPage = {
  items: Array<{
    id: string;
    name: string;
    description: string | null;
    images: Array<{ url: string }>;
    external_urls: { spotify: string };
    owner: { display_name: string | null };
    items?: { total: number };
    tracks?: { total: number };
  }>;
  next: string | null;
};

export async function GET() {
  try {
    const accessToken = await getSpotifyAccessToken();
    if (!accessToken) {
      return NextResponse.json({ error: "Sign in with Spotify to see your playlists." }, { status: 401 });
    }

    const playlists: Array<{
      id: string;
      name: string;
      description: string | null;
      image: string | null;
      url: string;
      owner: string | null;
      trackCount: number;
    }> = [];
    let url: string | null = "https://api.spotify.com/v1/me/playlists?limit=50";

    while (url) {
      const response: Response = await fetch(url, {
        headers: { Authorization: `Bearer ${accessToken}` },
        cache: "no-store",
      });
      if (!response.ok) {
        return NextResponse.json(
          { error: response.status === 403 ? "Spotify did not grant playlist access to this app." : "Spotify could not load your playlists." },
          { status: response.status },
        );
      }
      const page = (await response.json()) as SpotifyPlaylistPage;
      playlists.push(
        ...page.items.map((playlist) => ({
          id: playlist.id,
          name: playlist.name,
          description: playlist.description,
          image: playlist.images[0]?.url ?? null,
          url: playlist.external_urls.spotify,
          owner: playlist.owner.display_name,
          trackCount: playlist.items?.total ?? playlist.tracks?.total ?? 0,
        })),
      );
      url = page.next;
    }

    return NextResponse.json({ playlists });
  } catch {
    return NextResponse.json({ error: "Could not load Spotify playlists." }, { status: 502 });
  }
}

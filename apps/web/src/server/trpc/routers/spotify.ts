import { z } from "zod";
import {
  fetchAllPages,
  fetchPage,
  replacePlaylistTracks,
} from "@/server/spotify/client";
import { fetchPlaylistTracks } from "@/server/spotify/library";
import {
  LIKED_ID,
  likedPageSchema,
  type Playlist,
  type PlaylistTrack,
  playlistPageSchema,
  trackPageSchema,
} from "@/server/spotify/schema";
import { protectedProcedure, router } from "../trpc";

const API = "https://api.spotify.com/v1";

export const spotifyRouter = router({
  playlists: protectedProcedure.query(async ({ ctx }): Promise<Playlist[]> => {
    const [pages, liked] = await Promise.all([
      fetchAllPages(
        `${API}/me/playlists?limit=50`,
        ctx.spotifyAccessToken,
        playlistPageSchema,
      ),
      fetchPage(
        `${API}/me/tracks?limit=1`,
        ctx.spotifyAccessToken,
        likedPageSchema,
      ).catch(() => null),
    ]);
    const likedEntry: Playlist[] = liked
      ? [
          {
            id: LIKED_ID,
            name: "Liked Songs",
            description: "Tracks you saved on Spotify",
            image: null,
            url: "https://open.spotify.com/collection/tracks",
            owner: null,
            trackCount: liked.total,
          },
        ]
      : [];
    return [
      ...likedEntry,
      ...pages.flatMap((page) =>
        page.items.map((playlist) => ({
          id: playlist.id,
          name: playlist.name,
          description: playlist.description,
          image: playlist.images[0]?.url ?? null,
          url: playlist.external_urls.spotify,
          owner: playlist.owner.display_name,
          trackCount: playlist.items?.total ?? playlist.tracks?.total ?? 0,
        })),
      ),
    ];
  }),

  playlistTracks: protectedProcedure
    .input(z.object({ playlistId: z.string().min(1) }))
    .query(({ ctx, input }) =>
      fetchPlaylistTracks(ctx.spotifyAccessToken, input.playlistId),
    ),

  saveOrder: protectedProcedure
    .input(
      z.object({
        playlistId: z
          .string()
          .min(1)
          .refine((id) => id !== LIKED_ID, "Liked Songs cannot be reordered."),
        trackIds: z.array(z.string().min(1)).min(1).max(2000),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      await replacePlaylistTracks(
        `${API}/playlists/${encodeURIComponent(input.playlistId)}`,
        ctx.spotifyAccessToken,
        input.trackIds,
      );
      return { saved: input.trackIds.length };
    }),
});

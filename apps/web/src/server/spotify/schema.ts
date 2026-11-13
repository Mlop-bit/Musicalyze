import { z } from "zod";

const imageSchema = z.object({ url: z.string() });

export const spotifyProfileSchema = z.object({
  id: z.string(),
  account_id: z.string().optional(),
  display_name: z.string().nullish(),
  email: z.string().nullish(),
  images: z.array(imageSchema).default([]),
});

export const playlistPageSchema = z.object({
  items: z.array(
    z.object({
      id: z.string(),
      name: z.string(),
      description: z.string().nullable(),
      images: z.array(imageSchema),
      external_urls: z.object({ spotify: z.string() }),
      owner: z.object({ display_name: z.string().nullable() }),
      items: z.object({ total: z.number() }).optional(),
      tracks: z.object({ total: z.number() }).optional(),
    }),
  ),
  next: z.string().nullable(),
});

const trackItemSchema = z.object({
  id: z.string().nullable(),
  name: z.string(),
  duration_ms: z.number(),
  artists: z.array(z.object({ name: z.string() })),
  album: z.object({ name: z.string(), images: z.array(imageSchema) }),
  external_urls: z.object({ spotify: z.string() }),
  external_ids: z.object({ isrc: z.string().optional() }).optional(),
});

export const trackPageSchema = z.object({
  items: z.array(z.object({ item: trackItemSchema.nullable().catch(null) })),
  next: z.string().nullable(),
});

export const likedPageSchema = z.object({
  items: z.array(z.object({ track: trackItemSchema.nullable().catch(null) })),
  next: z.string().nullable(),
  total: z.number(),
});

export const LIKED_ID = "liked";

export const playlistSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().nullable(),
  image: z.string().nullable(),
  url: z.string(),
  owner: z.string().nullable(),
  trackCount: z.number(),
});

export const playlistTrackSchema = z.object({
  id: z.string().nullable(),
  name: z.string(),
  artists: z.string(),
  primaryArtist: z.string(),
  isrc: z.string().nullable(),
  album: z.string(),
  image: z.string().nullable(),
  url: z.string(),
  durationMs: z.number(),
});

export type Playlist = z.infer<typeof playlistSchema>;
export type PlaylistTrack = z.infer<typeof playlistTrackSchema>;

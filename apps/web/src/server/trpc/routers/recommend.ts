import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { pickCandidates } from "@/lib/candidates";
import { toDescriptors } from "@/lib/track-descriptors";
import {
  artistIdByTrackQuery,
  DEEZER_PREFIX,
  discoverFromSeeds,
  discoverTracks,
  hydrateDeezerTracks,
} from "@/server/deezer/discover";
import { assertJobOwner, recordJob } from "@/server/jobs/record";
import { callMl } from "@/server/ml/client";
import { jobCreatedSchema, recommendJobViewSchema } from "@/server/ml/schema";
import { appendPlaylistTracks, fetchAllPages } from "@/server/spotify/client";
import { fetchPlaylistTracks, hydrateTracks } from "@/server/spotify/library";
import { LIKED_ID, playlistPageSchema } from "@/server/spotify/schema";
import { protectedProcedure, router } from "../trpc";

const API = "https://api.spotify.com/v1";
const MAX_POOL_PLAYLISTS = 12;
const ANALYSIS_CANDIDATE_CAP = 40;
const ANALYSIS_ID_PREFIX = "search-";
const DISCOVER_CAP = 60;

const sourceSchema = z.enum(["library", "discover"]).default("library");

async function libraryPools(token: string, excludePlaylistId: string | null) {
  const library = await fetchAllPages(
    `${API}/me/playlists?limit=50`,
    token,
    playlistPageSchema,
  );
  const ids = [
    LIKED_ID,
    ...library.flatMap((page) => page.items.map((playlist) => playlist.id)),
  ]
    .filter((id) => id !== excludePlaylistId)
    .slice(0, MAX_POOL_PLAYLISTS);
  return Promise.all(
    ids.map((id) => fetchPlaylistTracks(token, id).catch(() => [])),
  );
}

export const recommendRouter = router({
  start: protectedProcedure
    .input(
      z.object({
        playlistId: z.string().min(1),
        trackId: z.string().min(1).optional(),
        title: z.string().min(1).max(200),
        source: sourceSchema,
        limit: z.number().int().min(5).max(50).default(20),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const token = ctx.spotifyAccessToken;
      const playlistTracks = await fetchPlaylistTracks(token, input.playlistId);
      const seeds = input.trackId
        ? playlistTracks.filter((track) => track.id === input.trackId)
        : playlistTracks;
      if (seeds.length === 0) {
        throw new TRPCError({
          code: "NOT_FOUND",
          message: "That track is not in this playlist anymore.",
        });
      }
      const candidates =
        input.source === "discover"
          ? await discoverFromSeeds(seeds, DISCOVER_CAP)
          : pickCandidates(seeds, [
              ...(await libraryPools(token, input.playlistId)),
              ...(input.trackId ? [playlistTracks] : []),
            ]);
      const created = await callMl("/jobs/recommend", jobCreatedSchema, {
        user_id: ctx.session.user.id,
        seeds: toDescriptors(seeds).map(descriptor),
        candidates: toDescriptors(candidates).map(descriptor),
        limit: input.limit,
      });
      await recordJob({
        id: created.job_id,
        userId: ctx.session.user.id,
        kind: "recommend",
        title: `${input.source === "discover" ? "Discover" : "Similar"} · ${input.title}`,
        playlistId: input.playlistId,
      });
      return {
        jobId: created.job_id,
        seeds: seeds.length,
        candidates: candidates.length,
      };
    }),

  similarToAnalysis: protectedProcedure
    .input(
      z.object({
        trackId: z.string().min(1),
        title: z.string().min(1).max(200),
        source: sourceSchema,
        limit: z.number().int().min(5).max(50).default(20),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      const candidates =
        input.source === "discover"
          ? await discoverTracks(
              [await artistIdByTrackQuery(input.title)].filter(
                (id): id is number => id !== null,
              ),
              new Set(),
              DISCOVER_CAP,
            )
          : pickCandidates(
              [],
              await libraryPools(ctx.spotifyAccessToken, null),
              ANALYSIS_CANDIDATE_CAP,
            );
      const created = await callMl("/jobs/recommend", jobCreatedSchema, {
        user_id: ctx.session.user.id,
        seeds: [{ track_id: input.trackId, title: input.title, artist: "" }],
        candidates: toDescriptors(candidates).map(descriptor),
        limit: input.limit,
      });
      await recordJob({
        id: created.job_id,
        userId: ctx.session.user.id,
        kind: "recommend",
        title: `${input.source === "discover" ? "Discover" : "Similar to"} ${input.title}`,
        playlistId: null,
      });
      return { jobId: created.job_id, candidates: candidates.length };
    }),

  job: protectedProcedure
    .input(z.object({ jobId: z.uuid() }))
    .query(async ({ ctx, input }) => {
      await assertJobOwner(ctx.session.user.id, input.jobId);
      const job = await callMl(`/jobs/${input.jobId}`, recommendJobViewSchema);
      const matches = job.result?.recommendations ?? [];
      const ids = matches
        .map((match) => match.track_id)
        .filter((id) => !id.startsWith(ANALYSIS_ID_PREFIX));
      const [spotify, deezer] = await Promise.all([
        hydrateTracks(
          ctx.spotifyAccessToken,
          ids.filter((id) => !id.startsWith(DEEZER_PREFIX)),
        ),
        hydrateDeezerTracks(ids.filter((id) => id.startsWith(DEEZER_PREFIX))),
      ]);
      const found = [...spotify, ...deezer];
      const byId = new Map(found.map((track) => [track.id, track]));
      const tracks = matches.flatMap((match) => {
        const track = byId.get(match.track_id);
        return track ? [{ ...track, similarity: match.similarity }] : [];
      });
      return {
        status: job.status,
        phase: job.phase,
        done: job.done,
        total: job.total,
        error: job.error,
        dropped: job.result?.dropped_candidates ?? 0,
        tracks,
      };
    }),

  addToPlaylist: protectedProcedure
    .input(
      z.object({
        playlistId: z
          .string()
          .min(1)
          .refine(
            (id) => id !== LIKED_ID,
            "Liked Songs cannot be extended here.",
          ),
        trackIds: z
          .array(
            z
              .string()
              .min(1)
              .refine(
                (id) => !id.startsWith(DEEZER_PREFIX),
                "Deezer tracks cannot be added to Spotify.",
              ),
          )
          .min(1)
          .max(100),
      }),
    )
    .mutation(async ({ ctx, input }) => {
      await appendPlaylistTracks(
        `${API}/playlists/${encodeURIComponent(input.playlistId)}`,
        ctx.spotifyAccessToken,
        input.trackIds,
      );
      return { added: input.trackIds.length };
    }),
});

function descriptor(entry: {
  trackId: string;
  title: string;
  artist: string;
  isrc: string | null;
}) {
  return {
    track_id: entry.trackId,
    title: entry.title,
    artist: entry.artist,
    isrc: entry.isrc,
  };
}
